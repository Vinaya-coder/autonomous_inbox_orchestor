from app.logic.reply_generator import ReplyGenerator
def test_ai():
    print("Testing AI Agent setup...")
    agent = ReplyGenerator()

    # 1. Test if the instructions are loaded
    print(f"\n--- System Instructions ---")
    print(agent.model._system_instruction.parts[0].text)

    # 2. Test if your personal info is loaded
    print(f"\n--- User Context ---")
    print(agent._load_user_context())

    # 3. Simulated Email
    fake_email = {"body": "Hey Vinaya, can we meet tomorrow at 5 PM?", "sender": "test@example.com"}
    print(f"\n--- Generating Test Reply ---")
    reply = agent.generate_reply(fake_email, db=None, thread_id="test_123")
    print(f"AI Reply: {reply}")


if __name__ == "__main__":
    test_ai()