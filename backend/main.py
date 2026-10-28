import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.db import init_db
from backend.seed import seed_database
from backend.routers import (
    students,
    syllabus,
    graph,
    diagnostic,
    lesson,
    teachback,
    flashcards,
    notes,
    dashboard,
    dev,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()

    # Attempt automatic seed loading if content is present
    try:
        seed_result = seed_database()
        print(f"[STARTUP] Seeded database: {seed_result}")
    except Exception as e:
        print(f"[STARTUP WARNING] Seed content could not be loaded at startup: {e}")

    yield


app = FastAPI(
    title="Gyaan Loop API",
    description="Adaptive AI Tutor Backend and Learning Engine",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standard structured error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail), "code": "HTTP_ERROR"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = "; ".join(f"{err.get('loc', [])}: {err.get('msg')}" for err in exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": error_msg, "code": "VALIDATION_ERROR"},
    )


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


# Mount all required routers
app.include_router(students.router)
app.include_router(syllabus.router)
app.include_router(graph.router)
app.include_router(diagnostic.router)
app.include_router(lesson.router)
app.include_router(teachback.router)
app.include_router(flashcards.router)
app.include_router(notes.router)
app.include_router(dashboard.router)
app.include_router(dev.router)
