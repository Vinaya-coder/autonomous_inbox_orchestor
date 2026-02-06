from app.services.email_agent import EmailAgent

if __name__ == "__main__":
    agent = EmailAgent()
    result = agent.run()
    print(result)
