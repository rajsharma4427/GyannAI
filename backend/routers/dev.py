from fastapi import APIRouter, HTTPException, status
from backend.contracts import AdvanceDaysRequest, AdvanceDaysResponse
from backend.db import get_db
from backend.engine import clock

router = APIRouter(prefix="/api/dev", tags=["dev"])


@router.post("/advance-days", response_model=AdvanceDaysResponse)
def advance_demo_days(req: AdvanceDaysRequest):
    if not isinstance(req.days, int) or req.days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Days must be a positive integer", "code": "INVALID_DAYS"},
        )

    with get_db() as conn:
        student = conn.execute("SELECT id FROM students WHERE id = ?", (req.student_id,)).fetchone()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Student '{req.student_id}' not found", "code": "STUDENT_NOT_FOUND"},
            )

        new_date_str = clock.advance_days(days=req.days, conn=conn)

    return AdvanceDaysResponse(new_date=new_date_str)
