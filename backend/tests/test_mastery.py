import pytest
from backend.engine.mastery import (
    update_mastery_on_answer,
    update_mastery_on_teachback,
    calculate_status,
)


def test_mastery_correct_answer():
    old = 0.5
    # mastery + (1 - mastery) * 0.3 = 0.5 + 0.5 * 0.3 = 0.65
    new = update_mastery_on_answer(old, is_correct=True)
    assert abs(new - 0.65) < 1e-4

    # From 0.0 -> 0.3
    assert abs(update_mastery_on_answer(0.0, is_correct=True) - 0.3) < 1e-4


def test_mastery_incorrect_answer_weights():
    # Careless: w = 0.15 -> 0.8 - (0.8 * 0.15) = 0.68
    m_careless = update_mastery_on_answer(0.8, is_correct=False, gap_type="careless")
    assert abs(m_careless - 0.68) < 1e-4

    # Procedural: w = 0.4 -> 0.8 - (0.8 * 0.4) = 0.48
    m_procedural = update_mastery_on_answer(0.8, is_correct=False, gap_type="procedural")
    assert abs(m_procedural - 0.48) < 1e-4

    # Conceptual: w = 0.5 -> 0.8 - (0.8 * 0.5) = 0.40
    m_conceptual = update_mastery_on_answer(0.8, is_correct=False, gap_type="conceptual")
    assert abs(m_conceptual - 0.40) < 1e-4

    # Prerequisite: w = 0.5 -> 0.8 - (0.8 * 0.5) = 0.40
    m_prereq = update_mastery_on_answer(0.8, is_correct=False, gap_type="prerequisite")
    assert abs(m_prereq - 0.40) < 1e-4


def test_mastery_teachback_equation():
    # mastery = 0.6 * old_mastery + 0.4 * score
    old = 0.5
    score = 0.9
    # 0.6 * 0.5 + 0.4 * 0.9 = 0.3 + 0.36 = 0.66
    new = update_mastery_on_teachback(old, score)
    assert abs(new - 0.66) < 1e-4


def test_mastery_status_thresholds_and_boundaries():
    assert calculate_status(0.0, has_activity=False) == "unseen"

    # Below 0.4 -> gap
    assert calculate_status(0.39, has_activity=True) == "gap"
    assert calculate_status(0.0, has_activity=True) == "gap"

    # Boundary at 0.4 -> learning
    assert calculate_status(0.40, has_activity=True) == "learning"
    assert calculate_status(0.60, has_activity=True) == "learning"

    # Boundary at 0.8 -> learning
    assert calculate_status(0.80, has_activity=True) == "learning"

    # Above 0.8 -> mastered
    assert calculate_status(0.81, has_activity=True) == "mastered"
    assert calculate_status(1.0, has_activity=True) == "mastered"
