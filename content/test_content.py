#!/usr/bin/env python3
"""Automated unit test suite for Person 4 content and validator.
Uses standard library unittest so it runs in any Python 3 environment.
"""
import json
import sys
import unittest
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent
if str(CONTENT_DIR) not in sys.path:
    sys.path.insert(0, str(CONTENT_DIR))

# Import explicitly from file path or local directory to avoid clash with system 'validate' package
import importlib.util
spec = importlib.util.spec_from_file_location("local_validate", CONTENT_DIR / "validate.py")
local_validate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local_validate)
validate = local_validate.validate
load = local_validate.load

class TestGyaanLoopContent(unittest.TestCase):

    def setUp(self):
        self.topics = load("syllabus_class10_math.json")
        self.questions = load("questions_seed.json")
        self.students = load("demo_students.json")

    def test_canonical_topics_count(self):
        """Must contain exactly 13 canonical topics."""
        self.assertEqual(len(self.topics), 13)

    def test_canonical_topic_ids(self):
        """Topic IDs must match the frozen canonical set."""
        expected = {
            "integers", "fractions", "algebraic_expressions", "linear_equations",
            "exponents", "polynomials", "factorization", "identities", "square_roots",
            "quadratic_equations", "solve_by_factorization", "quadratic_formula", "discriminant"
        }
        actual = {t["id"] for t in self.topics}
        self.assertEqual(actual, expected)

    def test_no_prerequisite_cycles(self):
        """Prerequisite relations must not contain cycles."""
        adj = {t["id"]: t["prereq_ids"] for t in self.topics}
        visited, visiting = set(), set()

        def dfs(node):
            self.assertNotIn(node, visiting, f"Prerequisite cycle detected at {node}")
            if node in visited:
                return
            visiting.add(node)
            for prereq in adj.get(node, []):
                dfs(prereq)
            visiting.remove(node)
            visited.add(node)

        for tid in adj:
            dfs(tid)

    def test_question_count_and_distribution(self):
        """Must have >= 39 questions, and >= 3 questions per topic across difficulties 1, 2, and 3."""
        self.assertGreaterEqual(len(self.questions), 39)
        topic_diffs = {}
        for q in self.questions:
            tid = q["topic_id"]
            if tid not in topic_diffs:
                topic_diffs[tid] = set()
            topic_diffs[tid].add(q["difficulty"])

        self.assertEqual(len(topic_diffs), 13)
        for tid, diffs in topic_diffs.items():
            self.assertTrue({1, 2, 3}.issubset(diffs), f"Topic {tid} missing difficulty 1, 2, or 3")

    def test_question_options_and_indices(self):
        """Every question must have 4 distinct options and correct_index in 0..3."""
        for q in self.questions:
            self.assertEqual(len(q["options"]), 4, f"{q['id']} must have exactly 4 options")
            self.assertEqual(len(set(q["options"])), 4, f"{q['id']} options must be unique")
            self.assertIn(q["correct_index"], (0, 1, 2, 3), f"{q['id']} correct_index must be 0-3")
            self.assertGreaterEqual(len(q["misconception_tags"]), 3, f"{q['id']} needs misconception tags")

    def test_demo_students(self):
        """Must include returning student with factorization/linear_equations gaps and new student."""
        self.assertGreaterEqual(len(self.students), 2)
        returning = next((s for s in self.students if len(s["starting_states"]) > 0), None)
        new_stu = next((s for s in self.students if len(s["starting_states"]) == 0), None)

        self.assertIsNotNone(returning, "Returning student fixture is missing")
        self.assertIsNotNone(new_stu, "New student fixture is missing")

        gap_topics = {st["topic_id"] for st in returning["starting_states"]}
        self.assertIn("factorization", gap_topics)
        self.assertIn("linear_equations", gap_topics)

    def test_full_validator_runs(self):
        """Validation script function must execute without raising exceptions."""
        try:
            validate()
        except Exception as exc:
            self.fail(f"validate() raised an unexpected error: {exc}")

if __name__ == "__main__":
    unittest.main()
