'''from app.database import SessionLocal
from app.models.email_models import ReplyContext

def main():
    db = SessionLocal()

    try:
        # 1. Clear existing contexts to prevent duplicates every time you run this
        print("Cleaning up old contexts...")
        db.query(ReplyContext).delete()

        # 2. Define all contexts in one list
        contexts = [
            # Personal info
            # Update these specific entries in your reply_contexts.py list:

            ReplyContext(
                context_type="personal",
                keywords="introduction,who am i",
                content="I am Vinaya, a software engineer intern at Imaginnovate. I'm currently working on AI automation projects!"
            ),
            ReplyContext(
                context_type="personal",
                keywords="cricket, hobbies, sports",
                content="I love watching and playing cricket! It's one of my favorite ways to spend my free time."
            ),
            ReplyContext(
                context_type="personal",
                keywords="plans, tonight, evening",
                content="I don't have anything fixed yet—probably just finishing some coding and then relaxing with a game of chess. How about you?"
            ),

            # Project info
            ReplyContext(
                context_type="project",
                keywords="email agent,auto-reply",
                content="I am currently working on the Email Auto-Reply Agent. "
                        "It monitors Gmail, generates replies using AI or templates, sends them, and logs everything in PostgreSQL."
            ),
            ReplyContext(
                context_type="project",
                keywords="status,progress",
                content="The Email Auto-Reply Agent is fully functional. Modules for reading emails, generating replies, and logging are working properly."
            ),
            ReplyContext(
                context_type="project",
                keywords="features,capabilities",
                content="The agent can read unread emails, generate AI or template replies, send emails, and log all interactions in the database."
            ),

            # Manager info
            ReplyContext(
                context_type="manager",
                keywords="manager,supervisor",
                content="My manager is Varaprasad, who oversees the Email Auto-Reply Agent project.",
                sender_email="varaprasadh.a@imaginnovate.com"
            ),
            ReplyContext(
                context_type="manager",
                keywords="meeting",
                content="Sure sir, let me check my calendar and get back to you.",
                sender_email="varaprasadh.a@imaginnovate.com"
            ),
            ReplyContext(
                context_type="manager",
                keywords="deadline",
                content="I will make sure to meet the deadline and update you shortly.",
                sender_email="varaprasadh.a@imaginnovate.com"
            ),

            # Fallback context
            ReplyContext(
                context_type="fallback",
                keywords="",
                content="Thank you for your email. Could you please clarify or provide more details?",
                sender_email=None
            )
        ]

        # 3. Add to DB and Commit inside the try block
        db.add_all(contexts)
        db.commit()
        print("✅ Database refreshed with latest reply contexts!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error updating contexts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()'''