import time
from app.core.email_agent import EmailAgent
from app.database import SessionLocal

if __name__ == "__main__":
    print("🚀 Email Agent started...")

    while True:
        db = SessionLocal()

        try:
            agent = EmailAgent(db=db)

            print("⏳ Checking inbox for new emails...")
            processed_count = agent.run()

            print(f"✅ Processed {processed_count} new emails.\n")

        except Exception as e:
            print(f"⚠ Error while running agent: {e}")
        finally:
            db.close()

        print("⏳ Sleeping for 30 seconds...\n")
        time.sleep(30)