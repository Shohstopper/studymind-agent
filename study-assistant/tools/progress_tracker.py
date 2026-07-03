"""
Progress Tracker Tool
Local tools for saving and retrieving study goals, quiz results, and notes.
These wrap the MCP server tools for use in the ADK agent context.
"""

import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
GOALS_FILE = DATA_DIR / "goals.json"
QUIZ_FILE = DATA_DIR / "quiz_history.json"


def _load(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_study_goal(subject: str, target_date: str, daily_hours: float = 1.0, notes: str = "") -> str:
    """
    Save a study goal for a subject.
    
    Args:
        subject: The subject or topic to study
        target_date: Target completion date in YYYY-MM-DD format
        daily_hours: Hours per day planned for studying
        notes: Any additional notes about the goal
    
    Returns:
        Confirmation message
    """
    goals = _load(GOALS_FILE)
    goals[subject] = {
        "target_date": target_date,
        "daily_hours": daily_hours,
        "notes": notes,
        "completed": False,
        "created_at": datetime.now().isoformat(),
    }
    _save(GOALS_FILE, goals)
    return f"Goal saved: Study '{subject}' by {target_date} ({daily_hours}h/day)"


def get_study_goals() -> str:
    """
    Retrieve all saved study goals and their status.
    
    Returns:
        Formatted string of all study goals
    """
    goals = _load(GOALS_FILE)
    if not goals:
        return "No study goals saved yet."
    lines = ["Your Study Goals:", ""]
    for subject, data in goals.items():
        status = "Complete" if data["completed"] else "In Progress"
        lines.append(f"- {subject}: {status} | Due: {data['target_date']} | {data['daily_hours']}h/day")
    return "\n".join(lines)


def mark_goal_complete(subject: str) -> str:
    """
    Mark a study goal as completed.
    
    Args:
        subject: The subject name to mark as complete
    
    Returns:
        Confirmation message
    """
    goals = _load(GOALS_FILE)
    if subject not in goals:
        return f"No goal found for '{subject}'. Check your goals list."
    goals[subject]["completed"] = True
    goals[subject]["completed_at"] = datetime.now().isoformat()
    _save(GOALS_FILE, goals)
    return f"Marked '{subject}' as complete! Great work!"


def get_progress_summary() -> str:
    """
    Get an overall summary of learning progress.
    
    Returns:
        Summary of goals completed, quizzes taken, and average scores
    """
    goals = _load(GOALS_FILE)
    history = _load(QUIZ_FILE)
    completed = sum(1 for g in goals.values() if g["completed"])
    total_quizzes = sum(len(a) for a in history.values())
    avg_score = 0.0
    if history:
        all_scores = [a["score"] for attempts in history.values() for a in attempts]
        avg_score = sum(all_scores) / len(all_scores)
    return (
        f"Progress Summary:\n"
        f"- Goals: {completed}/{len(goals)} completed\n"
        f"- Quizzes taken: {total_quizzes}\n"
        f"- Average quiz score: {avg_score:.1f}%\n"
        f"{'Keep going, you are doing great!' if avg_score >= 70 else 'Keep practicing!'}"
    )


def save_quiz_result(topic: str, score: float, total_questions: int, correct_answers: int, weak_areas: list = None) -> str:
    """
    Save a quiz result.
    
    Args:
        topic: The topic of the quiz
        score: Score as a percentage (0-100)
        total_questions: Total number of questions in the quiz
        correct_answers: Number of questions answered correctly
        weak_areas: List of sub-topics to review
    
    Returns:
        Confirmation with encouragement
    """
    history = _load(QUIZ_FILE)
    if topic not in history:
        history[topic] = []
    history[topic].append({
        "score": score,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "weak_areas": weak_areas or [],
        "timestamp": datetime.now().isoformat(),
    })
    _save(QUIZ_FILE, history)
    msg = f"Quiz saved: {score:.0f}% on '{topic}' ({correct_answers}/{total_questions} correct)"
    if weak_areas:
        msg += f"\nAreas to review: {', '.join(weak_areas)}"
    return msg


def get_quiz_history() -> str:
    """
    Get past quiz results and performance trends.
    
    Returns:
        Formatted quiz history with averages and trends
    """
    history = _load(QUIZ_FILE)
    if not history:
        return "No quiz history yet. Take your first quiz!"
    lines = ["Quiz History:", ""]
    for topic, attempts in history.items():
        avg = sum(a["score"] for a in attempts) / len(attempts)
        latest = attempts[-1]
        trend = "improving" if len(attempts) > 1 and attempts[-1]["score"] > attempts[-2]["score"] else "steady"
        lines.append(f"- {topic}: {len(attempts)} attempts | Avg: {avg:.1f}% | Trend: {trend}")
        lines.append(f"  Latest: {latest['score']}% ({latest['correct_answers']}/{latest['total_questions']})")
    return "\n".join(lines)
