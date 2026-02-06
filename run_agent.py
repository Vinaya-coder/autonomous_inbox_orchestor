import time
from app.services.email_agent import EmailAgent

if __name__ == "__main__":
    print("📨 Email Agent started...")

    while True:
        print("⏳ Checking inbox for new emails...")

        try:

            agent = EmailAgent()

            result = agent.run()
            processed = result.get("processed", 0)

            # Close the connection after each run
            agent.db.close()

            print(f"✅ Processed {processed} new emails.\n")
        except Exception as e:
            print(f"⚠ Error while running agent: {e}")

        print("⏳ Sleeping for 30 seconds...\n")
        time.sleep(30)