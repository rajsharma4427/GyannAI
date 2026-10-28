from typing import Optional
from backend.contracts import Question, GapItem

MAX_DIAGNOSTIC_QUESTIONS = 8


def next_difficulty(current_diff: int, is_correct: bool) -> int:
    """Adjust difficulty: correct increases up to 3, incorrect decreases down to 1."""
    if is_correct:
        return min(3, current_diff + 1)
    else:
        return max(1, current_diff - 1)


def should_stop_diagnostic(
    questions_answered: int,
    root_gaps: list[dict],
    is_correct_on_prereq: bool = False,
) -> bool:
    """Check if diagnostic session should terminate:
    - 8 questions answered
    - Root gap reached and confirmed
    - Correct answer reached on a prerequisite (demonstrating the root is solid)
    """
    if questions_answered >= MAX_DIAGNOSTIC_QUESTIONS:
        return True
    if len(root_gaps) >= 2:
        return True
    if is_correct_on_prereq and len(root_gaps) >= 1:
        return True
    return False
