import pytest
from backend.contracts import MistakeAnalysis
from backend.engine.backtrace import evaluate_backtrace_step, MAX_BACKTRACE_DEPTH


def test_backtrace_valid_prerequisite():
    analysis = MistakeAnalysis(
        gap_type="prerequisite",
        suspected_prereq_id="factorization",
        reason="Struggling with middle term splitting",
    )
    next_topic, bt_info, gap = evaluate_backtrace_step(
        analysis=analysis,
        current_topic_id="quadratic_equations",
        allowed_prereq_ids=["factorization", "polynomials"],
        visited_topics=["quadratic_equations"],
        current_depth=1,
    )
    assert next_topic == "factorization"
    assert bt_info is not None
    assert bt_info.from_topic_id == "quadratic_equations"
    assert bt_info.to_topic_id == "factorization"
    assert "middle term" in bt_info.reason
    assert gap is None


def test_backtrace_rejects_unlisted_prerequisite():
    analysis = MistakeAnalysis(
        gap_type="prerequisite",
        suspected_prereq_id="trigonometry",
        reason="Trigonometry issue",
    )
    next_topic, bt_info, gap = evaluate_backtrace_step(
        analysis=analysis,
        current_topic_id="quadratic_equations",
        allowed_prereq_ids=["factorization", "polynomials"],
        visited_topics=["quadratic_equations"],
        current_depth=1,
    )
    # Unlisted prereq is rejected -> marks current topic as gap
    assert next_topic is None
    assert bt_info is None
    assert gap == "prerequisite"


def test_backtrace_stops_at_max_depth_3():
    analysis = MistakeAnalysis(
        gap_type="prerequisite",
        suspected_prereq_id="polynomials",
        reason="Needs basics",
    )
    next_topic, bt_info, gap = evaluate_backtrace_step(
        analysis=analysis,
        current_topic_id="factorization",
        allowed_prereq_ids=["polynomials"],
        visited_topics=["quadratic_equations", "solve_by_factorization", "factorization"],
        current_depth=3,  # Already at max depth 3!
    )
    assert next_topic is None
    assert bt_info is None
    assert gap == "prerequisite"


def test_backtrace_prevents_cycles():
    analysis = MistakeAnalysis(
        gap_type="prerequisite",
        suspected_prereq_id="factorization",
        reason="Loop",
    )
    next_topic, bt_info, gap = evaluate_backtrace_step(
        analysis=analysis,
        current_topic_id="polynomials",
        allowed_prereq_ids=["factorization"],
        visited_topics=["quadratic_equations", "factorization"],  # factorization already visited!
        current_depth=2,
    )
    assert next_topic is None
    assert bt_info is None
    assert gap == "prerequisite"
