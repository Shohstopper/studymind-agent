"""
Security & Input Validation Layer
Protects the system from prompt injection, abusive inputs, and unauthorized operations.
"""

import re
from typing import Tuple

# Max characters allowed per user message
MAX_INPUT_LENGTH = 4000

# Patterns that indicate prompt injection or jailbreak attempts
INJECTION_PATTERNS = [
    r"ignore (previous|all|above) instructions",
    r"you are now",
    r"act as (a|an|the)",
    r"forget (your|all) (instructions|rules|guidelines)",
    r"disregard (your|all)",
    r"system prompt",
    r"<\|.*?\|>",           # Token-style injections
    r"\[INST\]",             # Instruction tags
    r"###\s*(Human|Assistant|System):",  # Role-play injections
]

# Topics outside the study assistant's scope
OUT_OF_SCOPE_PATTERNS = [
    r"\b(hack|exploit|vulnerability|malware|virus)\b",
    r"\b(weapon|bomb|poison)\b",
    r"\b(password|credit card|ssn|social security)\b",
]

# Compiled patterns for performance
_INJECTION_RE = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
_SCOPE_RE = [re.compile(p, re.IGNORECASE) for p in OUT_OF_SCOPE_PATTERNS]


def validate_input(user_input: str) -> Tuple[bool, str]:
    """
    Validate user input for safety and appropriateness.
    
    Args:
        user_input: The raw user message
    
    Returns:
        Tuple of (is_valid: bool, message: str)
        If invalid, message explains the issue.
        If valid, message is the sanitized input.
    """
    if not user_input or not user_input.strip():
        return False, "Please enter a message."
    
    # Length check
    if len(user_input) > MAX_INPUT_LENGTH:
        return False, f"Message too long. Please keep it under {MAX_INPUT_LENGTH} characters."
    
    # Prompt injection check
    for pattern in _INJECTION_RE:
        if pattern.search(user_input):
            return False, (
                "I noticed something in your message that looks like an attempt to override my instructions. "
                "I'm here to help you study — please ask me a study-related question!"
            )
    
    # Out-of-scope check
    for pattern in _SCOPE_RE:
        if pattern.search(user_input):
            return False, (
                "That topic is outside what I can help with. "
                "I'm specialized in study assistance — ask me about any subject you're learning!"
            )
    
    # Sanitize: strip leading/trailing whitespace, normalize spaces
    sanitized = re.sub(r"\s+", " ", user_input.strip())
    
    return True, sanitized


def sanitize_output(agent_response: str) -> str:
    """
    Sanitize agent output before displaying to the user.
    Removes any accidentally included sensitive patterns.
    
    Args:
        agent_response: Raw agent response
    
    Returns:
        Sanitized response string
    """
    # Remove any API keys or tokens that might appear (defensive)
    response = re.sub(r"[A-Za-z0-9]{32,}", lambda m: m.group() if " " in m.group() else "[REDACTED]", agent_response)
    return response


def rate_limit_check(session_id: str, request_count: dict, max_requests: int = 50) -> Tuple[bool, str]:
    """
    Simple in-memory rate limiting per session.
    
    Args:
        session_id: Unique session identifier
        request_count: Dict tracking requests per session
        max_requests: Max requests allowed per session
    
    Returns:
        Tuple of (is_allowed: bool, message: str)
    """
    count = request_count.get(session_id, 0)
    if count >= max_requests:
        return False, "You've reached the request limit for this session. Please start a new session."
    request_count[session_id] = count + 1
    return True, "OK"
