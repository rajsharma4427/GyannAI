from typing import Literal, Optional
from backend.contracts import GapType

StatusType = Literal["unseen", "gap", "learning", "mastered"]

MISTAKE_WEIGHTS: dict[GapType, float] = {
    "careless": 0.15,
    "procedural": 0.4,
    "conceptual": 0.5,
    "prerequisite": 0.5,
}


def clamp(val: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    return max(min_val, min(max_val, round(val, 4)))


def update_mastery_on_answer(
    current_mastery: float,
    is_correct: bool,
    gap_type: Optional[GapType] = None,
) -> float:
    """Update mastery based on answer correctness and gap type.
    
    Correct:
      mastery = mastery + (1 - mastery) * 0.3
    Incorrect:
      mastery = mastery - mastery * w
      where w is determined by gap_type (careless=0.15, procedural=0.4, conceptual=0.5, prerequisite=0.5).
    """
    if is_correct:
        new_mastery = current_mastery + (1.0 - current_mastery) * 0.3
    else:
        weight = MISTAKE_WEIGHTS.get(gap_type, 0.4) if gap_type else 0.4
        new_mastery = current_mastery - (current_mastery * weight)
    return clamp(new_mastery)


def update_mastery_on_teachback(current_mastery: float, score: float) -> float:
    """Update mastery from teach-back score:
    mastery = 0.6 * old_mastery + 0.4 * score
    """
    new_mastery = 0.6 * current_mastery + 0.4 * score
    return clamp(new_mastery)


def calculate_status(mastery: float, has_activity: bool = True) -> StatusType:
    """Determine topic status based on mastery and activity evidence.
    
    Status thresholds:
    - 'unseen' if no learning activity
    - 'gap' if mastery < 0.4
    - 'learning' if 0.4 <= mastery <= 0.8
    - 'mastered' if mastery > 0.8
    """
    if not has_activity:
        return "unseen"
    if mastery < 0.4:
        return "gap"
    if mastery <= 0.8:
        return "learning"
    return "mastered"


def update_confidence(current_confidence: float, step: float = 0.2) -> float:
    """Confidence increases with learning evidence up to 1.0."""
    return clamp(current_confidence + step)
