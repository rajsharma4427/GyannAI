from datetime import date, timedelta
from typing import NamedTuple


class SRSResult(NamedTuple):
    interval_days: int
    ease: float
    repetitions: int
    next_review: str


def calculate_sm2(
    quality: int,
    current_interval: int,
    current_ease: float,
    repetitions: int,
    today_str: str,
) -> SRSResult:
    """Calculate next SM-2 interval, ease, and review date.
    
    Quality q in [0, 5]:
    - If q < 3: interval resets to 1 day, repetitions resets to 0.
    - If q >= 3:
      - repetitions == 0 -> interval = 1, repetitions = 1
      - repetitions == 1 -> interval = 6, repetitions = 2
      - repetitions >= 2 -> interval = round(previous_interval * ease), repetitions += 1
    - Ease update:
      ease = max(1.3, ease + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    - next_review = today + timedelta(days=interval_days)
    """
    if quality < 0 or quality > 5:
        raise ValueError(f"Quality must be between 0 and 5, got {quality}")

    # Calculate new ease factor
    diff = 5 - quality
    new_ease = current_ease + 0.1 - (diff * (0.08 + diff * 0.02))
    new_ease = max(1.3, round(new_ease, 4))

    if quality < 3:
        new_interval = 1
        new_repetitions = 0
    else:
        if repetitions == 0:
            new_interval = 1
            new_repetitions = 1
        elif repetitions == 1:
            new_interval = 6
            new_repetitions = 2
        else:
            new_interval = max(1, round(current_interval * new_ease))
            new_repetitions = repetitions + 1

    current_d = date.fromisoformat(today_str)
    next_review_d = current_d + timedelta(days=new_interval)

    return SRSResult(
        interval_days=new_interval,
        ease=new_ease,
        repetitions=new_repetitions,
        next_review=next_review_d.isoformat(),
    )
