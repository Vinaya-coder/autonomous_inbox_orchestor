import os
import google.generativeai as genai
from app.models.email_models import ChatHistory
from app.providers.calendar_tool import create_meeting


class ReplyGenerator:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No Gemini API key found")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=[create_meeting],
            system_instruction=(
                "ROLE: You are Vinaya's professional executive assistant.\n"
                "KNOWLEDGE: Use provided 'Vinaya's INFO' to answer questions.\n\n"

                "SCHEDULING RULES:\n"
                "1. If the user mentions a specific time (e.g., 5 PM, 11:30 AM), you MUST use that exact time for the 'create_meeting' tool.\n"
                "2. ONLY suggest 4 PM if the user is completely vague and doesn't mention a time at all.\n"
                "3. If 'create_meeting' returns 'ALREADY_BOOKED', do not apologize and quit; instead, tell the user that slot is taken and suggest an alternative.\n"
                "4. When 'create_meeting' is successful, the tool returns a 'hangoutLink'. You MUST copy this link exactly into your email reply. A response without the link is considered a failure.\n"
                "5. Always extract all email addresses from the conversation to include as attendees.\n\n"

                "RESCHEDULING: If a user wants to change a meeting, call 'create_meeting' for the new time immediately."
            )
        )
        self.info_file = "vinaya_info.txt"
    def _get_vinaya_knowledge(self) -> str:
        if os.path.exists(self.info_file):
            with open(self.info_file, 'r') as f:
                return f.read()
        return "Vinaya is a software engineer intern."

    def save_chat(self, db, thread_id: str, role: str, content: str):
        new_entry = ChatHistory(thread_id=thread_id, role=role, content=content)
        db.add(new_entry)
        db.commit()

    def generate_reply(self, email_obj, db, thread_id: str, calendar_service=None, thread_history: list = None) -> str:
        vinaya_info = self._get_vinaya_knowledge()
        body_str = str(email_obj.get("body", ""))
        sender = email_obj.get("sender", "")

        chat = self.model.start_chat(history=thread_history or [], enable_automatic_function_calling=True)

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        prompt = f"Current Time: {now}\nVinaya's INFO: {vinaya_info}\nSENDER: {sender}\nUSER MESSAGE: {body_str}"

        try:
            response = chat.send_message(prompt)
            reply_text = response.text.strip()
            return reply_text

        except Exception as e:
            import traceback
            print("\n--- 🚨 AI GENERATION ERROR ---")
            traceback.print_exc()
            print("-----------------------------\n")

            # If the error is about Auth, tell the user (or yourself)
            if "auth" in str(e).lower():
                return "My calendar access has expired. Please re-authenticate me!"

            return "I'm looking into that for you and will get back to you shortly."