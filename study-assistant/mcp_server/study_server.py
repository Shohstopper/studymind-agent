"""
StudyMind MCP Server
Exposes study tools as MCP-compatible endpoints for agent consumption.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Data storage path
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
GOALS_FILE = DATA_DIR / "goals.json"
QUIZ_FILE = DATA_DIR / "quiz_history.json"
NOTES_FILE = DATA_DIR / "notes.json"

app = Server("studymind-server")


def _load_json(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save_json(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="save_study_goal",
            description="Save a study goal with subject, target date, and daily hours",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Subject or topic name"},
                    "target_date": {"type": "string", "description": "Target completion date (YYYY-MM-DD)"},
                    "daily_hours": {"type": "number", "description": "Hours per day to study"},
                    "notes": {"type": "string", "description": "Additional notes about the goal"},
                },
                "required": ["subject", "target_date"],
            },
        ),
        Tool(
            name="get_study_goals",
            description="Retrieve all study goals and their completion status",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="mark_goal_complete",
            description="Mark a study goal as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Subject name to mark complete"},
                },
                "required": ["subject"],
            },
        ),
        Tool(
            name="save_quiz_result",
            description="Save a quiz result with score and topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Quiz topic"},
                    "score": {"type": "number", "description": "Score as percentage (0-100)"},
                    "total_questions": {"type": "integer", "description": "Total number of questions"},
                    "correct_answers": {"type": "integer", "description": "Number of correct answers"},
                    "weak_areas": {"type": "array", "items": {"type": "string"}, "description": "Topics to review"},
                },
                "required": ["topic", "score", "total_questions", "correct_answers"],
            },
        ),
        Tool(
            name="get_quiz_history",
            description="Get past quiz results and performance trends",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="save_note",
            description="Save a study note for a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic the note is about"},
                    "content": {"type": "string", "description": "Note content"},
                    "format": {"type": "string", "description": "Format: bullet_points, flashcards, mind_map"},
                },
                "required": ["topic", "content"],
            },
        ),
        Tool(
            name="get_notes",
            description="Retrieve saved notes, optionally filtered by topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Filter by topic (optional)"},
                },
            },
        ),
        Tool(
            name="get_progress_summary",
            description="Get overall learning progress summary across all subjects",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "save_study_goal":
        goals = _load_json(GOALS_FILE)
        subject = arguments["subject"]
        goals[subject] = {
            "target_date": arguments["target_date"],
            "daily_hours": arguments.get("daily_hours", 1),
            "notes": arguments.get("notes", ""),
            "completed": False,
            "created_at": datetime.now().isoformat(),
        }
        _save_json(GOALS_FILE, goals)
        return [TextContent(type="text", text=f"✅ Goal saved: {subject} by {arguments['target_date']}")]

    elif name == "get_study_goals":
        goals = _load_json(GOALS_FILE)
        if not goals:
            return [TextContent(type="text", text="No study goals saved yet.")]
        result = "📚 **Your Study Goals:**\n\n"
        for subject, data in goals.items():
            status = "✅ Complete" if data["completed"] else "🔄 In Progress"
            result += f"**{subject}** — {status}\n"
            result += f"  Target: {data['target_date']} | {data['daily_hours']}h/day\n"
            if data["notes"]:
                result += f"  Notes: {data['notes']}\n"
            result += "\n"
        return [TextContent(type="text", text=result)]

    elif name == "mark_goal_complete":
        goals = _load_json(GOALS_FILE)
        subject = arguments["subject"]
        if subject in goals:
            goals[subject]["completed"] = True
            goals[subject]["completed_at"] = datetime.now().isoformat()
            _save_json(GOALS_FILE, goals)
            return [TextContent(type="text", text=f"🎉 Marked '{subject}' as complete!")]
        return [TextContent(type="text", text=f"Goal '{subject}' not found.")]

    elif name == "save_quiz_result":
        history = _load_json(QUIZ_FILE)
        topic = arguments["topic"]
        if topic not in history:
            history[topic] = []
        history[topic].append({
            "score": arguments["score"],
            "total_questions": arguments["total_questions"],
            "correct_answers": arguments["correct_answers"],
            "weak_areas": arguments.get("weak_areas", []),
            "timestamp": datetime.now().isoformat(),
        })
        _save_json(QUIZ_FILE, history)
        return [TextContent(type="text", text=f"📊 Quiz result saved: {arguments['score']}% on {topic}")]

    elif name == "get_quiz_history":
        history = _load_json(QUIZ_FILE)
        if not history:
            return [TextContent(type="text", text="No quiz history yet. Take a quiz to get started!")]
        result = "📊 **Quiz History:**\n\n"
        for topic, attempts in history.items():
            avg_score = sum(a["score"] for a in attempts) / len(attempts)
            latest = attempts[-1]
            result += f"**{topic}**\n"
            result += f"  Attempts: {len(attempts)} | Avg Score: {avg_score:.1f}%\n"
            result += f"  Latest: {latest['score']}% ({latest['correct_answers']}/{latest['total_questions']})\n"
            if latest.get("weak_areas"):
                result += f"  Review: {', '.join(latest['weak_areas'])}\n"
            result += "\n"
        return [TextContent(type="text", text=result)]

    elif name == "save_note":
        notes = _load_json(NOTES_FILE)
        topic = arguments["topic"]
        if topic not in notes:
            notes[topic] = []
        notes[topic].append({
            "content": arguments["content"],
            "format": arguments.get("format", "bullet_points"),
            "saved_at": datetime.now().isoformat(),
        })
        _save_json(NOTES_FILE, notes)
        return [TextContent(type="text", text=f"📝 Note saved for '{topic}'")]

    elif name == "get_notes":
        notes = _load_json(NOTES_FILE)
        topic_filter = arguments.get("topic")
        if topic_filter:
            if topic_filter not in notes:
                return [TextContent(type="text", text=f"No notes found for '{topic_filter}'.")]
            result = f"📝 **Notes for {topic_filter}:**\n\n"
            for note in notes[topic_filter]:
                result += f"{note['content']}\n\n---\n"
            return [TextContent(type="text", text=result)]
        if not notes:
            return [TextContent(type="text", text="No notes saved yet.")]
        result = "📝 **All Notes:**\n\n" + "\n".join(f"• {t} ({len(n)} notes)" for t, n in notes.items())
        return [TextContent(type="text", text=result)]

    elif name == "get_progress_summary":
        goals = _load_json(GOALS_FILE)
        history = _load_json(QUIZ_FILE)
        notes = _load_json(NOTES_FILE)
        completed = sum(1 for g in goals.values() if g["completed"])
        total_quizzes = sum(len(a) for a in history.values())
        avg_quiz_score = 0
        if history:
            all_scores = [a["score"] for attempts in history.values() for a in attempts]
            avg_quiz_score = sum(all_scores) / len(all_scores)
        summary = f"""📈 **Your Learning Progress Summary**

🎯 Study Goals: {completed}/{len(goals)} completed
📊 Quizzes Taken: {total_quizzes} | Avg Score: {avg_quiz_score:.1f}%
📝 Note Sets Saved: {len(notes)}

{'🔥 Great progress! Keep it up!' if avg_quiz_score >= 70 else '💪 Keep practicing — you are improving!'}
"""
        return [TextContent(type="text", text=summary)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
