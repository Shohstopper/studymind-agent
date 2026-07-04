"""
Root Orchestrator Agent
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from tools.progress_tracker import (
    save_study_goal, get_study_goals, get_progress_summary,
    save_quiz_result, get_quiz_history
)

MODEL = LiteLlm(model="groq/llama-3.3-70b-versatile", drop_params=True)

from agents.planner_agent import planner_agent
from agents.summarizer_agent import summarizer_agent
from agents.quiz_agent import quiz_agent

root_agent = LlmAgent(
    name="StudyMind_Orchestrator",
    model=MODEL,
    description="Multi-agent study assistant — plans, explains, and quizzes",
    instruction="""You are StudyMind, a study assistant with three modes:

STUDY PLANNING: If the student wants a schedule or plan — ask for subject, deadline, hours per day. Build a realistic day-by-day plan. Save the goal using save_study_goal.

SUMMARIZING: If the student wants something explained — ask how they want it (bullet points, flashcards, paragraph, full breakdown). Explain clearly without padding.

QUIZZING: If the student wants to be tested — ask for topic and number of questions (default 5). Mix formats. After each answer explain why. Save the result using save_quiz_result.

Use get_study_goals and get_progress_summary for progress checks. Use get_quiz_history for past quiz results.
Figure out what the student needs and handle it directly.""",
    tools=[save_study_goal, get_study_goals, get_progress_summary, save_quiz_result, get_quiz_history],
)
