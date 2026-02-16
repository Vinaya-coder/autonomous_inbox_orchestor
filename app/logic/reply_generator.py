import os
import shutil
from datetime import datetime
import google.generativeai as genai

from app.config import settings
from app.models.email_models import AttachmentRecord
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
            system_instruction=settings.get_instructions()
        )
        self.user_info_path = settings.USER_INFO_FILE
        self.base_url = os.environ.get("BASE_URL", "http://localhost:8000")

    def _load_user_context(self) -> str:
        try:
            if os.path.exists(self.user_info_path):
                with open(self.user_info_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            return "The user is a software professional named Vinaya."
        except Exception as e:
            print(f"Error loading context file: {e}")
            return "The user is a software professional."

    def save_to_local_storage(self, file_path):
        target_dir = os.path.join(os.getcwd(), "static", "attachments")
        os.makedirs(target_dir, exist_ok=True)
        filename = os.path.basename(file_path)
        final_path = os.path.join(target_dir, filename)

        shutil.move(file_path, final_path)
        return f"{self.base_url}/static/attachments/{filename}"

    def generate_reply(self, email_obj, db, thread_id=None, attachments: list = None, thread_history: list = None,
                       calendar_service=None):
        vinaya_info = self._load_user_context()
        final_thread_id = str(email_obj.get("thread_id") or thread_id or "unknown")
        sender_email = str(email_obj.get("sender", "unknown"))

        _ = [thread_history, calendar_service]

        body_str = str(email_obj.get("body", ""))
        stored_urls = []

        if attachments:
            for path in attachments:
                if os.path.exists(path):
                    public_url = self.save_to_local_storage(path)
                    if public_url:
                        try:
                            new_rec = AttachmentRecord(
                                thread_id=final_thread_id,
                                sender_email=sender_email,
                                file_name=os.path.basename(path),
                                url=public_url
                            )
                            db.add(new_rec)
                            stored_urls.append(public_url)
                        except Exception as e:
                            print(f"❌ DB Error: {e}")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat = self.model.start_chat(history=[], enable_automatic_function_calling=True)

        prompt = (
            f"Current Time: {now}\n"
            f"Context: {vinaya_info}\n"
            f"Email from: {sender_email}\n"
            f"Message: {body_str}\n\n"
            f"Note: {len(stored_urls)} files were saved. URLs: {stored_urls}"
        )

        try:
            response = chat.send_message(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI Error: {e}")
            return None

    def _cleanup_temp(self):
        temp_folder = "temp_attachments"
        if os.path.exists(temp_folder):
            for filename in os.listdir(temp_folder):
                file_path = os.path.join(temp_folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Cleanup error: {e}")