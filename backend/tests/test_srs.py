import pytest
from datetime import date, timedelta
from backend.engine.srs import calculate_sm2


def test_sm2_first_success():
    # rep 0, q = 4
    today = "2026-10-28"
    res = calculate_sm2(
        quality=4,
        current_interval=0,
        current_ease=2.5,
        repetitions=0,
        today_str=today,
    )
    assert res.interval_days == 1
    assert res.repetitions == 1
    assert res.next_review == "2026-10-29"
    # ease change for q=4: diff=1 -> 2.5 + 0.1 - 1*(0.08 + 0.02) = 2.5 + 0.1 - 0.10 = 2.5
    assert abs(res.ease - 2.5) < 1e-3


def test_sm2_second_success():
    # rep 1, q = 5 -> interval = 6
    today = "2026-10-28"
    res = calculate_sm2(
        quality=5,
        current_interval=1,
        current_ease=2.5,
        repetitions=1,
        today_str=today,
    )
    assert res.interval_days == 6
    assert res.repetitions == 2
    assert res.next_review == "2026-11-03"
    # ease change for q=5: diff=0 -> 2.5 + 0.1 = 2.6
    assert abs(res.ease - 2.6) < 1e-3


def test_sm2_subsequent_success():
    # rep 2, q = 4, interval = 6, ease = 2.5 -> round(6 * 2.5) = 15
    today = "2026-10-28"
    res = calculate_sm2(
        quality=4,
        current_interval=6,
        current_ease=2.5,
        repetitions=2,
        today_str=today,
    )
    assert res.interval_days == 15
    assert res.repetitions == 3
    assert res.next_review == "2026-11-12"


def test_sm2_failure_resets_interval_and_reps():
    # quality < 3 (e.g. 2 or 1)
    today = "2026-10-28"
    res = calculate_sm2(
        quality=2,
        current_interval=15,
        current_ease=2.5,
        repetitions=3,
        today_str=today,
    )
    assert res.interval_days == 1
    assert res.repetitions == 0
    assert res.next_review == "2026-10-29"


def test_sm2_minimum_ease_floor():
    # Minimum ease is 1.3
    today = "2026-10-28"
    res = calculate_sm2(
        quality=0,
        current_interval=1,
        current_ease=1.35,
        repetitions=0,
        today_str=today,
    )
    assert res.ease >= 1.3


def test_sm2_invalid_quality():
    with pytest.raises(ValueError):
        calculate_sm2(quality=6, current_interval=1, current_ease=2.5, repetitions=0, today_str="2026-10-28")
    with pytest.raises(ValueError):
        calculate_sm2(quality=-1, current_interval=1, current_ease=2.5, repetitions=0, today_str="2026-10-28")
