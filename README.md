# 🧠 StudyMind — Multi-Agent Study Assistant

> A capstone project for the [5-Day AI Agents: Intensive Vibe Coding Course with Google](https://www.kaggle.com/competitions/vibecoding-agents-capstone-project)
> **Track: Concierge Agents**

StudyMind is a multi-agent AI system that acts as your personal study companion. It combines four specialized agents — an orchestrator, a study planner, a content summarizer, and a quiz generator — all powered by Google ADK and LiteLLM with Groq.

---

## 🎯 Problem Statement

Students struggle with three core challenges: **knowing what to study**, **understanding difficult content**, and **retaining what they've learned**. Existing tools address these separately. StudyMind unifies them into a single, intelligent, conversational agent system.

---

## 🏗️ Architecture

```
User Input
    │
    ▼
[Security Layer] ── Validates & sanitizes input
    │
    ▼
[Root Orchestrator Agent] ── Routes to specialized agents
    ├──► [Study Planner Agent] ── Schedules, goals, deadlines
    │         └── Tools: save_goal, get_goals, mark_complete, progress_summary
    │
    ├──► [Summarizer Agent] ── Explains & condenses content
    │         └── Tools: web_search, fetch_page_content
    │
    └──► [Quiz Master Agent] ── Tests knowledge, tracks scores
              └── Tools: save_quiz_result, get_quiz_history
                    │
                    ▼
             [Custom MCP Server] ── Persistent data layer
                    │
                    ▼
              [Local JSON Store] ── Goals, quiz history, notes
```

---

## ✅ Key Concepts Demonstrated

| Concept | Where |
|---|---|
| **Multi-Agent System (ADK)** | 4 agents: Orchestrator + 3 specialists |
| **MCP Server** | `mcp_server/study_server.py` — 7 custom tools |
| **Agent Skills** | Summarization, quiz generation, planning |
| **Security Features** | Input validation, prompt injection detection, rate limiting, URL sanitization |
| **Deployability** | Gradio UI, runs locally or on any cloud VM |

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- A Google API Key ([get one here](https://aistudio.google.com/apikey))

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/studymind-agent.git
cd studymind-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 5. Run the app
python main.py          # Web UI at http://localhost:7860
python main.py --cli    # Terminal mode
```

---

## 💬 Example Interactions

**Study Planning:**
> "Create a 7-day study plan for Python basics. I have 2 hours per day."

**Summarization:**
> "Summarize machine learning in flashcard format."

**Quizzing:**
> "Quiz me on data structures — 5 intermediate questions."

**Progress Tracking:**
> "Show me my progress summary."

---

## 🔒 Security Features

- **Prompt injection detection** — blocks attempts to override agent instructions
- **Input length limiting** — max 4,000 characters per message
- **URL sanitization** — blocks internal/private network access in web fetch tool
- **Output sanitization** — scrubs any accidental sensitive data from responses
- **In-session rate limiting** — max 50 requests per session

---

## 📁 Project Structure

```
studymind-agent/
├── main.py                   # Entry point (UI or CLI)
├── requirements.txt
├── .env.example
├── agents/
│   ├── root_agent.py         # Orchestrator
│   ├── planner_agent.py      # Study planner
│   ├── summarizer_agent.py   # Content summarizer
│   └── quiz_agent.py         # Quiz generator
├── mcp_server/
│   └── study_server.py       # Custom MCP server (7 tools)
├── tools/
│   ├── web_search.py         # Web search + page fetch
│   └── progress_tracker.py   # Goal & quiz tracking
├── security/
│   └── input_validator.py    # Security layer
├── ui/
│   └── app.py                # Gradio web interface
└── data/                     # Local JSON storage (auto-created)
```

---

## 👥 Team

Built for the Kaggle AI Agents Capstone Project — 5-Day AI Agents: Intensive Vibe Coding Course with Google.
Team Members- 
1. Shoheb Akter Khan
2. Sahani Shakya

---

## 📄 License

CC-BY 4.0 — Open for reuse with attribution.
