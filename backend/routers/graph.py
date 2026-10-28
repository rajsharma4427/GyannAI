from fastapi import APIRouter, HTTPException, status
from backend.contracts import GraphResponse, Topic, TopicState
from backend.db import get_db

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/{student_id}", response_model=GraphResponse)
def get_student_graph(student_id: str):
    with get_db() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

        # Get all topics
        topic_rows = conn.execute("SELECT id, name, parent_id, description FROM topics ORDER BY rowid").fetchall()
        
        # Get all prerequisites
        prereq_rows = conn.execute("SELECT topic_id, prereq_id FROM topic_prereqs").fetchall()
        prereqs_map: dict[str, list[str]] = {}
        for pr in prereq_rows:
            prereqs_map.setdefault(pr["topic_id"], []).append(pr["prereq_id"])

        topics: list[Topic] = []
        for tr in topic_rows:
            topics.append(
                Topic(
                    id=tr["id"],
                    name=tr["name"],
                    parent_id=tr["parent_id"],
                    prereq_ids=prereqs_map.get(tr["id"], []),
                    description=tr["description"] or "",
                )
            )

        # Get student's states
        state_rows = conn.execute(
            """
            SELECT topic_id, mastery, confidence, gap_type, interval_days, ease, next_review, status
            FROM topic_state
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchall()

        existing_states: dict[str, TopicState] = {}
        for sr in state_rows:
            existing_states[sr["topic_id"]] = TopicState(
                topic_id=sr["topic_id"],
                mastery=sr["mastery"],
                confidence=sr["confidence"],
                gap_type=sr["gap_type"],
                interval_days=sr["interval_days"],
                ease=sr["ease"],
                next_review=sr["next_review"],
                status=sr["status"],
            )

        # Ensure all topics have a TopicState for this student
        states: list[TopicState] = []
        for t in topics:
            if t.id in existing_states:
                states.append(existing_states[t.id])
            else:
                # Default unseen state
                states.append(
                    TopicState(
                        topic_id=t.id,
                        mastery=0.0,
                        confidence=0.0,
                        gap_type=None,
                        interval_days=0,
                        ease=2.5,
                        next_review=None,
                        status="unseen",
                    )
                )

    return GraphResponse(topics=topics, states=states)
