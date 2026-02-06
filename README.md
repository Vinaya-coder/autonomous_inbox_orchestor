# Autonomous Inbox Orchestrator

An intelligent, headless AI agent designed to manage professional communications and scheduling. 
The system uses **Gemini 2.0 Flash** to reason through unstructured email data and execute 
calendar actions autonomously.

## 🚀 Key Features
* **Intent Recognition:** Automatically distinguishes between general inquiries and scheduling requests.
* **Autonomous Scheduling:** Coordinates meetings by checking availability and creating Google Calendar invites.
* **Context Persistence:** Maintains multi-turn conversation history using a relational database (SQLAlchemy).
* **Automated Triage:** Filters and processes incoming Gmail threads without human intervention.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **AI Model:** Google Gemini 2.0 Flash
* **APIs:** Gmail API, Google Calendar API
* **Database:** SQLite / SQLAlchemy (State Management)

## 📦 Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your `.env` file with your Gemini API Key.
4. Run the agent: `python run_agent.py`