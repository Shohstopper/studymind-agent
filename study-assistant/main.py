"""
StudyMind — Multi-Agent Study Assistant
Entry point for running the application.

Usage:
    python main.py          # Launch Gradio web UI
    python main.py --cli    # Run in terminal mode
"""

import argparse
import asyncio
import os
import uuid

from dotenv import load_dotenv
load_dotenv()

# Validate required env vars
if not os.getenv("GOOGLE_API_KEY"):
    raise EnvironmentError(
        "GOOGLE_API_KEY is not set. Please add it to your .env file.\n"
        "Get your key at: https://aistudio.google.com/apikey"
    )


def run_ui():
    """Launch the Gradio web interface."""
    from ui.app import create_ui
    print("Starting StudyMind Web UI at http://localhost:7860")
    app = create_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)


async def run_cli():
    """Run StudyMind in CLI mode for quick testing."""
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    from agents.root_agent import root_agent
    from security.input_validator import validate_input, sanitize_output

    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name="StudyMind", session_service=session_service)
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name="StudyMind", user_id="user", session_id=session_id)

    print("\n🧠 StudyMind CLI — Multi-Agent Study Assistant")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye! Keep studying! 📚")
            break

        is_valid, processed = validate_input(user_input)
        if not is_valid:
            print(f"⚠️  {processed}\n")
            continue

        content = types.Content(role="user", parts=[types.Part(text=processed)])
        print("StudyMind: ", end="", flush=True)
        async for event in runner.run_async(user_id="user", session_id=session_id, new_message=content):
            if event.is_final_response() and event.content and event.content.parts:
                response = sanitize_output(event.content.parts[0].text)
                print(response)
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StudyMind Multi-Agent Study Assistant")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode instead of web UI")
    args = parser.parse_args()

    if args.cli:
        asyncio.run(run_cli())
    else:
        run_ui()
