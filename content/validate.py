#!/usr/bin/env python3
"""Validate Person 4's seed files against the Gyaan Loop shared contract.

Uses only Python's standard library so it can run independently before teammates'
packages or databases exist. The schema checks mirror Section 3 of the build plan
and backend/contracts.py.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent

def load(name: str):
    path = ROOT / name
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        raise ValueError(f"Could not read valid JSON from {path}: {exc}") from exc

def require(condition: bool, message: str):
    if not condition:
        raise ValueError(message)

def validate():
    print("--> Starting Gyaan Loop content validation...")
    topics = load("syllabus_class10_math.json")
    questions = load("questions_seed.json")
    students = load("demo_students.json")

    # 1. Syllabus array check
    require(isinstance(topics, list), "syllabus_class10_math.json must be a JSON array")
    require(len(topics) == 13, f"exactly 13 canonical topics required, found {len(topics)}")

    # 2. Topic fields and unique canonical IDs
    topic_ids = set()
    topic_by_id = {}
    for i, t in enumerate(topics):
        for field in ("id", "name", "prereq_ids", "description"):
            require(field in t, f"topic[{i}] missing required field: {field}")
        require(isinstance(t["id"], str) and t["id"].strip(), f"topic[{i}] id must be a non-empty string")
        require(t["id"] not in topic_ids, f"duplicate topic id: {t['id']}")
        require(isinstance(t["name"], str) and t["name"].strip(), f"topic {t['id']} name must be non-empty")
        require(isinstance(t["description"], str) and t["description"].strip(), f"topic {t['id']} description must be non-empty")
        require(isinstance(t["prereq_ids"], list), f"{t['id']}.prereq_ids must be a list")
        topic_ids.add(t["id"])
        topic_by_id[t["id"]] = t

    canonical = {
        "integers", "fractions", "algebraic_expressions", "linear_equations",
        "exponents", "polynomials", "factorization", "identities", "square_roots",
        "quadratic_equations", "solve_by_factorization", "quadratic_formula", "discriminant"
    }
    require(
        topic_ids == canonical,
        f"topic IDs differ from canonical set; missing={sorted(canonical - topic_ids)}, extra={sorted(topic_ids - canonical)}"
    )

    # 3. Prerequisite validity
    for t in topics:
        for prereq in t["prereq_ids"]:
            require(prereq in topic_ids, f"topic '{t['id']}' references unknown prerequisite '{prereq}'")
            require(prereq != t["id"], f"topic '{t['id']}' cannot be a prerequisite of itself")

    # 4. Cycle detection using DFS
    visiting, visited = set(), set()
    def visit(tid):
        if tid in visiting:
            raise ValueError(f"prerequisite cycle detected involving topic '{tid}'")
        if tid in visited:
            return
        visiting.add(tid)
        for prereq in topic_by_id[tid]["prereq_ids"]:
            visit(prereq)
        visiting.remove(tid)
        visited.add(tid)

    for tid in topic_ids:
        visit(tid)

    # 5. Questions shape and count checks
    require(isinstance(questions, list), "questions_seed.json must be a JSON array")
    require(len(questions) >= 39, f"at least 39 questions required, found {len(questions)}")

    counts = defaultdict(int)
    qids = set()
    for i, q in enumerate(questions):
        for field in ("id", "topic_id", "stem", "options", "correct_index", "difficulty", "misconception_tags"):
            require(field in q, f"question[{i}] missing required field: {field}")
        require(isinstance(q["id"], str) and q["id"].strip(), f"question[{i}] id must be non-empty")
        require(q["id"] not in qids, f"duplicate question id: {q['id']}")
        qids.add(q["id"])
        require(q["topic_id"] in topic_ids, f"question '{q['id']}' references unknown topic '{q['topic_id']}'")
        require(isinstance(q["stem"], str) and q["stem"].strip(), f"question '{q['id']}' stem must be non-empty")
        require(isinstance(q["options"], list) and len(q["options"]) == 4,
                f"question '{q['id']}' must have exactly four options")
        for opt_idx, opt in enumerate(q["options"]):
            require(isinstance(opt, str) and opt.strip(), f"question '{q['id']}' option[{opt_idx}] must be non-empty")
        require(len(set(q["options"])) == 4, f"question '{q['id']}' options must be distinct")
        require(isinstance(q["correct_index"], int) and 0 <= q["correct_index"] <= 3,
                f"question '{q['id']}' correct_index must be an integer between 0 and 3")
        require(q["difficulty"] in (1, 2, 3), f"question '{q['id']}' difficulty must be 1, 2, or 3")
        require(isinstance(q["misconception_tags"], list) and len(q["misconception_tags"]) >= 3,
                f"question '{q['id']}' misconception_tags must be a list with at least 3 distractor tags")
        for tag in q["misconception_tags"]:
            require(isinstance(tag, str) and tag.strip(), f"question '{q['id']}' has empty misconception tag")
        counts[q["topic_id"]] += 1

    # 6. Per-topic question and difficulty coverage
    for tid in sorted(topic_ids):
        require(counts[tid] >= 3, f"topic '{tid}' has fewer than 3 questions (has {counts[tid]})")
        diffs = {q["difficulty"] for q in questions if q["topic_id"] == tid}
        require({1, 2, 3}.issubset(diffs), f"topic '{tid}' must have questions for difficulties 1, 2, and 3")

    # 7. Demo students validation
    require(isinstance(students, list) and len(students) >= 2,
            "demo_students.json must be a list containing at least 2 demo students")

    student_ids = set()
    returning_student = None
    new_student = None

    for i, student in enumerate(students):
        for field in ("student_id", "name", "lang", "starting_states"):
            require(field in student, f"demo_students[{i}] missing required field: {field}")
        require(isinstance(student["student_id"], str) and student["student_id"].strip(),
                f"demo_students[{i}] student_id must be non-empty")
        require(student["student_id"] not in student_ids, f"duplicate demo student id: {student['student_id']}")
        student_ids.add(student["student_id"])
        require(student["lang"] in ("en", "hi", "hinglish"),
                f"invalid lang '{student['lang']}' for student {student['student_id']}")
        require(isinstance(student["starting_states"], list),
                f"{student['student_id']}.starting_states must be a list")

        if len(student["starting_states"]) > 0:
            returning_student = student
        else:
            new_student = student

        for state in student["starting_states"]:
            for state_field in ("topic_id", "mastery", "confidence"):
                require(state_field in state, f"{student['student_id']} state missing {state_field}")
            require(state["topic_id"] in topic_ids,
                    f"{student['student_id']} state references unknown topic '{state['topic_id']}'")
            require(0.0 <= float(state["mastery"]) <= 1.0,
                    f"{student['student_id']} mastery must be between 0.0 and 1.0")
            require(0.0 <= float(state["confidence"]) <= 1.0,
                    f"{student['student_id']} confidence must be between 0.0 and 1.0")
            if "status" in state:
                require(state["status"] in ("unseen", "gap", "learning", "mastered"),
                        f"invalid state status '{state['status']}'")
            if "gap_type" in state and state["gap_type"] is not None:
                require(state["gap_type"] in ("conceptual", "procedural", "careless", "prerequisite"),
                        f"invalid gap_type '{state['gap_type']}'")

    require(returning_student is not None, "one demo student must be a returning student with learning history")
    require(new_student is not None, "one demo student must be a new student with no prior history")

    # Verify specific weaknesses in Student 1 (returning student)
    ret_gaps = {s["topic_id"] for s in returning_student["starting_states"]}
    require("factorization" in ret_gaps,
            "Student 1 must have starting state for 'factorization' demonstrating weakness")
    require("linear_equations" in ret_gaps,
            "Student 1 must have starting state for 'linear_equations' demonstrating weakness")

    print(f"PASS: 13 canonical topics verified with zero prerequisite cycles.")
    print(f"PASS: {len(questions)} seed questions verified across all 13 topics covering difficulties 1, 2, and 3.")
    print(f"PASS: {len(students)} demo students validated (returning student with gaps + new student).")
    print(f"PASS: All content files strictly adhere to Gyaan Loop contracts.")
    return True

validate_content = validate

if __name__ == "__main__":
    try:
        validate()
        sys.exit(0)
    except Exception as exc:
        print(f"\nVALIDATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
