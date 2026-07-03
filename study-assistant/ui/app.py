"""
StudyMind Gradio Web Interface
Provides a clean, interactive UI for the multi-agent study assistant.
"""

import asyncio
import uuid
import gradio as gr
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.root_agent import root_agent
from security.input_validator import validate_input, sanitize_output, rate_limit_check

# Session tracking for rate limiting
_request_counts: dict = {}

# ADK Runner setup
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="StudyMind",
    session_service=session_service,
)

APP_DESCRIPTION = """
# 🧠 StudyMind — Multi-Agent Study Assistant

Your personal AI-powered study companion. Ask me to:
- 📅 **Plan** your study schedule for any subject
- 📖 **Summarize** any topic or article
- ❓ **Quiz** you on what you've learned
- 📊 **Track** your progress over time
"""


async def chat(message: str, history: list, session_id: str) -> tuple:
    """Process a user message through the multi-agent system."""
    # Security validation
    is_valid, processed = validate_input(message)
    if not is_valid:
        history.append((message, f"⚠️ {processed}"))
        return "", history

    # Rate limiting
    allowed, rate_msg = rate_limit_check(session_id, _request_counts)
    if not allowed:
        history.append((message, f"⚠️ {rate_msg}"))
        return "", history

    # Ensure session exists
    existing = session_service.get_session(app_name="StudyMind", user_id="user", session_id=session_id)
    if not existing:
        session_service.create_session(app_name="StudyMind", user_id="user", session_id=session_id)

    # Run through ADK agent
    content = types.Content(role="user", parts=[types.Part(text=processed)])
    response_text = ""
    try:
        async for event in runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text
    except Exception as e:
        response_text = f"An error occurred: {str(e)}. Please try again."

    response_text = sanitize_output(response_text)
    history.append((message, response_text))
    return "", history


def create_ui():
    with gr.Blocks(
        title="StudyMind — Multi-Agent Study Assistant",
        theme=gr.themes.Soft(primary_hue="blue"),
        css="""
        .chatbot { height: 500px; }
        .session-info { font-size: 0.8em; color: #666; }
        """,
    ) as demo:
        session_id = gr.State(lambda: str(uuid.uuid4()))

        gr.Markdown(APP_DESCRIPTION)

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="StudyMind",
                    elem_classes=["chatbot"],
                    avatar_images=("👤", "🧠"),
                    bubble_full_width=False,
                )
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask me anything about your studies...",
                        label="",
                        scale=4,
                        autofocus=True,
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)

            with gr.Column(scale=1):
                gr.Markdown("### 💡 Quick Start")
                examples = gr.Examples(
                    examples=[
                        ["Create a 7-day study plan for Python basics. I have 2 hours per day."],
                        ["Summarize the concept of machine learning in flashcard format."],
                        ["Quiz me on data structures — 5 intermediate questions."],
                        ["Show me my progress summary."],
                        ["I have a calculus exam in 3 days. Help me plan!"],
                        ["Explain neural networks like I'm a beginner."],
                    ],
                    inputs=msg,
                    label="",
                )

                gr.Markdown("### 🤖 Your Agents")
                gr.Markdown("""
**📅 Study Planner**
Creates schedules & tracks goals

**📖 Summarizer**  
Explains & summarizes any topic

**❓ Quiz Master**
Tests your knowledge & tracks scores
                """)

        # Event handlers
        msg.submit(chat, [msg, chatbot, session_id], [msg, chatbot])
        send_btn.click(chat, [msg, chatbot, session_id], [msg, chatbot])

        gr.Markdown(
            "<div class='session-info'>StudyMind uses Google ADK, Gemini 2.0 Flash, and a custom MCP server. "
            "Your progress is saved locally.</div>"
        )

    return demo


if __name__ == "__main__":
    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
