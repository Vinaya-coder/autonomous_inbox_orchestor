import os
import re
import dateparser
from datetime import datetime, timedelta
import google.generativeai as genai
from app.models.email_models import ChatHistory
from app.services.calendar_tool import create_meeting, is_slot_busy


class ReplyGenerator:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("No Gemini/Google API key found in environment")

        genai.configure(api_key=api_key)

        # Updated instructions to allow flexible scheduling
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=(
                "You are Vinaya's professional assistant. Use the provided INFO to answer questions about project status and work. "
                "For scheduling: "
                "1. If the user wants to meet but doesn't give a time, use [[SCHEDULE]] and say you'll pick a slot. "
                "2. If the user says they are busy, acknowledge it and ask for a new time. "
                "3. If they provide a new time, use [[SCHEDULE]]."
            )
        )
        self.info_file = "vinaya_info.txt"

    def _get_vinaya_knowledge(self) -> str:
        if os.path.exists(self.info_file):
            with open(self.info_file, 'r') as f:
                return f.read()
        return "I am Vinaya, a software engineer intern."

    def _extract_time(self, text: str):
        """Extracts time if mentioned, otherwise returns None."""
        dt = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
        if dt and any(char.isdigit() for char in text):
            if dt < datetime.now(): dt += timedelta(days=1)
            return dt

        match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?', text, re.IGNORECASE)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2) or 0)
            ampm = match.group(3)
            if ampm and ampm.upper() == "PM" and hour != 12:
                hour += 12
            elif ampm and ampm.upper() == "AM" and hour == 12:
                hour = 0
            dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            if dt < datetime.now(): dt += timedelta(days=1)
            return dt
        return None

    def get_history_for_thread(self, db, thread_id: str):
        logs = db.query(ChatHistory).filter(ChatHistory.thread_id == thread_id).order_by(
            ChatHistory.created_at.asc()).all()
        return [{"role": log.role, "parts": [log.content]} for log in logs]

    def save_chat(self, db, thread_id: str, role: str, content: str):
        new_entry = ChatHistory(thread_id=thread_id, role=role, content=content)
        db.add(new_entry)
        db.commit()

    def generate_reply(self, email_obj, db, thread_id: str, calendar_service=None, thread_history: list = None) -> str:
        raw_history = thread_history if thread_history else self.get_history_for_thread(db, thread_id)
        clean_history = []

        for entry in raw_history:
            text_parts = [str(p) for p in entry.get("parts", []) if p is not None]
            if text_parts:
                clean_history.append({"role": entry["role"], "parts": text_parts})

        # 2. Get the current message
        raw_body = email_obj.get("body", "")
        body_str = str(raw_body) if raw_body else "No content"
        sender = str(email_obj.get("sender", "")).lower()
        vinaya_info = str(self._get_vinaya_knowledge())

        chat = self.model.start_chat(history=clean_history)
        history = thread_history if thread_history else self.get_history_for_thread(db, thread_id)
        chat = self.model.start_chat(history=clean_history)
        prompt = f"Vinaya's INFO: {vinaya_info}\n\nUSER MESSAGE: {body_str}"

        try:
            self.save_chat(db, thread_id, "user", body_str)
            response = chat.send_message(prompt, generation_config={"temperature": 0.0})
            reply_text = response.text.strip()

            if "[[SCHEDULE]]" in reply_text:
                new_dt = self._extract_time(body_str)

                if new_dt is None:
                    new_dt = datetime.now() + timedelta(hours=1)
                    if new_dt.hour > 18:  # If it's too late, suggest tomorrow morning
                        new_dt = new_dt.replace(hour=10) + timedelta(days=1)

                start_time_iso = new_dt.replace(microsecond=0).isoformat() + "+05:30"

                # Check Conflict
                if calendar_service and is_slot_busy(calendar_service, start_time_iso):
                    # Try 1 hour later if busy
                    new_dt += timedelta(hours=1)
                    start_time_iso = new_dt.replace(microsecond=0).isoformat() + "+05:30"

                meet_link = create_meeting("Meeting with Vinaya", sender, start_time_iso)

                if meet_link:
                    time_str = new_dt.strftime("%I:%M %p")
                    reply_text = reply_text.replace("[[SCHEDULE]]",
                                                    f"\n\nI've scheduled this for {time_str}. Link: {meet_link}")
                else:
                    reply_text = reply_text.replace("[[SCHEDULE]]", "\n\nI'll check my calendar and ping you soon!")

            self.save_chat(db, thread_id, "model", reply_text)
            return reply_text


        except Exception as e:

            error_msg = str(e)

            if "429" in error_msg or "quota" in error_msg.lower():
                print("🛑 STOPPING: Quota is over. Not sending email to avoid spamming.")
                return None  # Return None so the EmailSender doesn't trigger
            print(f"❌ Actual Logic Error: {e}")
            return "I'll check the schedule and get back to you shortly."