# Gyaan Loop — Adaptive AI Mathematics Tutor

> **6-Hour AI Hackathon MVP** · Complete 4-Person Integration & Verification

Gyaan Loop is an adaptive AI-powered mathematics learning platform focused on Class 10 CBSE Mathematics. When a student struggles with an advanced question, Gyaan Loop uses prerequisite DAG backtracing to find and resolve the root-cause conceptual or procedural gap rather than repeating failed drills.

---

## 1. Team Architecture & Ownership

| Component | Owner | Technologies | Directory |
| :--- | :--- | :--- | :--- |
| **AI Engine** | Person 1 | Python, Pydantic v2, SQLite Cache, Anthropic Claude / Input-Aware Mock | `ai_engine/` |
| **Backend & Learning Engine** | Person 2 | FastAPI, SQLite (WAL mode), SM-2 SRS, Prerequisite Backtrace | `backend/` |
| **Frontend Student Experience** | Person 3 | React 18, TypeScript, Vite, React Router, Zustand, Lucide | `frontend/` |
| **Voice, Content & Pitch** | Person 4 | Web Speech API, CBSE Class 10 Seed Data (13 topics, 39 questions), Deck | `content/`, `pitch/` |

---

## 2. Quickstart on Windows (PowerShell)

### Prerequisites
- **Python 3.10+** (tested and verified on Python 3.14.0)
- **Node.js 18+** & **npm** (tested and verified on Node v24.13.1 / npm 11.8.0)

### One-Click Launch

Open two PowerShell windows:

#### Terminal 1 — Start the Backend
```powershell
.\start-backend.ps1
```
*Or manually:*
```powershell
$env:PYTHONPATH = "."
$env:AI_MOCK = "1"
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

#### Terminal 2 — Start the Frontend
```powershell
.\start-frontend.ps1
```
*Or manually:*
```powershell
cd frontend
npm run dev
```

---

## 3. Local Application URLs

- **Student Web Application:** [http://localhost:5173](http://localhost:5173)
- **Backend API Root:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive OpenAPI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Backend Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 4. Configuration & Modes

Gyaan Loop is configured to run **100% locally out-of-the-box without requiring API keys**.

### Backend Modes (`.env`)
- **Deterministic Mock Mode (Default for Demos & Testing):**
  `AI_MOCK=1`
  Uses the input-aware mock engine in `ai_engine/mock.py`. Exercises the complete system deterministically with realistic Class 10 CBSE Math feedback, mistake diagnosis, lesson explanations, and teach-back evaluation.
- **Live LLM Provider Mode:**
  `AI_MOCK=0`
  Set `ANTHROPIC_API_KEY=your_key_here` in `.env`. Calls Claude models with automatic retry, exponential backoff, and SQLite-backed response caching (`AI_CACHE=1`).

### Frontend Modes (`frontend/.env`)
- **Connected / Integrated Mode (Default):**
  ```dotenv
  VITE_MOCK=false
  VITE_API_BASE_URL=http://127.0.0.1:8000
  ```
  All requests route to the FastAPI backend at `http://127.0.0.1:8000`.
- **Frontend Standalone Demo Mode:**
  ```dotenv
  VITE_MOCK=true
  ```
  Runs the React application using client-side in-memory mock adapters without requiring the backend server.

---

## 5. Automated Verification & Test Commands

Every component has been verified with automated tests:

### 1. Backend & Integration Tests (62 tests passing)
```powershell
pytest backend/tests -p no:cacheprovider
```

### 2. AI Engine Unit & Contract Tests (16 tests passing)
```powershell
pytest -c ai_engine/pytest.ini ai_engine/tests
```

### 3. Content Validation & Integrity Tests (7 tests passing)
```powershell
python content/validate.py
python content/test_content.py
```

### 4. Frontend Type Checking & Tests
```powershell
cd frontend
npm run typecheck   # 0 TypeScript errors
npm test            # 6 Vitest tests passing
npm run build       # Clean production build to dist/
```

### 5. Complete 18-Step End-to-End User Journey
```powershell
pytest backend/tests/test_e2e_journey.py -v -p no:cacheprovider
```

---

## 6. End-to-End 18-Step Journey

The automated test suite (`backend/tests/test_e2e_journey.py`) verifies the entire user lifecycle:

1. **System Health Check** (`GET /health`) → Confirms server and database status.
2. **Deterministic Database Seeding** (`backend/seed.py`) → Loads 13 canonical topics, 39 seed questions, and demo learners.
3. **Student Profile Creation** (`POST /api/students`) → Registers new student with chosen language (English, Hindi, Hinglish).
4. **Syllabus Draft & Ingestion** (`POST /api/syllabus`) → Generates and maps 13 canonical Class 10 topics.
5. **Initial Knowledge DAG Retrieval** (`GET /api/graph/{student_id}`) → Retrieves 13 topics and baseline mastery states.
6. **Diagnostic Session Initiation** (`POST /api/diagnostic/start`) → Loads first diagnostic question for target topic.
7. **Intentional Incorrect Answer Submission** (`POST /api/diagnostic/answer`) → Submits incorrect option to trigger error analysis.
8. **Prerequisite Backtrace Activation** → AI engine identifies missing prerequisite (`factorization`) and navigates backward.
9. **Prerequisite Question Delivery** → Serves targeted prerequisite question to isolate the root-cause gap.
10. **Prerequisite Diagnostic Completion** → Completes diagnostic with gap classification recorded.
11. **Adaptive Lesson Retrieval** (`GET /api/lesson/{student_id}/{topic_id}`) → Delivers story, explanation, key terms, and practice.
12. **Interactive Multimodal Teach-Back** (`POST /api/teachback`) → Evaluates student's verbal/written conceptual explanation.
13. **Dynamic Flashcard Generation** → Automatically creates SM-2 spaced repetition cards for unmastered concepts.
14. **Personal Note Generation & Storage** (`POST /api/notes`) → AI and student reflection notes saved to SQLite.
15. **Due Flashcard Queue Inspection** (`GET /api/flashcards/due/{student_id}`) → Verifies newly generated review items.
16. **SM-2 Flashcard Review Execution** (`POST /api/flashcards/review`) → Calculates next interval and ease factor based on review quality.
17. **Demo Clock Advancement** (`POST /api/dev/advance-days`) → Fast-forwards demo clock to bring scheduled reviews due.
18. **Final Dashboard Metrics Verification** (`GET /api/dashboard/{student_id}`) → Verifies mastery progression, streaks, and weakest topics.
