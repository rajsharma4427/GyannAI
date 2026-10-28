# Gyaan Loop — Backup Demonstration Recording Plan

**Purpose:** Comprehensive guide and timestamped shot list for recording `pitch/backup_demo.mp4` on the demo laptop, ensuring a flawless visual backup if live Wi-Fi or hardware fails during the pitch.

---

## 1. Recording Setup & Specifications

- **Target Output File:** `pitch/backup_demo.mp4`
- **Resolution:** 1080p (1920 × 1080) at 30 fps or 60 fps
- **Aspect Ratio:** 16:9
- **Display Scale:** 100% (or browser zoom at 110% for crisp visibility of math formulas)
- **Audio Capture:** Built-in microphone or headset mic (clear vocal recording, minimal background noise)
- **Browser:** Google Chrome (Desktop) in full-screen / clean window (bookmarks bar hidden, extensions disabled)
- **Recommended Tools:**
  - **Linux / Ubuntu:** Built-in GNOME screen recorder (`Ctrl + Alt + Shift + R`), OBS Studio, or `simplescreenrecorder`.
  - **Windows:** Xbox Game Bar (`Win + Alt + R`) or OBS Studio.
  - **macOS:** QuickTime Screen Recording (`Cmd + Shift + 5`).

### Pre-Recording Checklist
1. Start backend server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   *(Or with `AI_MOCK=1 uvicorn backend.main:app --port 8000` for guaranteed fast, deterministic mock responses)*
2. Start frontend dev server:
   ```bash
   cd frontend && npm run dev
   ```
3. Open `http://localhost:5173` in Google Chrome.
4. Verify audio output is enabled (for browser speech synthesis).
5. Grant microphone permission to `http://localhost:5173` in Chrome settings.
6. Run `python content/validate.py` once to confirm content store integrity.

---

## 2. Timestamped Shot List (0:00 – 4:00)

### Shot 1: Title Screen & Core Problem
- **Timestamp:** 0:00 – 0:30 (Duration: 30s)
- **Frame:** Gyaan Loop Home / Welcome Dashboard.
- **Visual Action:**
  - Cursor rests cleanly near the top logo.
  - Smoothly highlights the Class 10 Mathematics header.
- **Audio Cue / Voiceover:**
  - *"Welcome to Gyaan Loop. In Class 10 mathematics, when a student gets a question wrong, traditional platforms merely show a red cross. But math is a prerequisite ladder: errors in quadratics almost always stem from cracks in factorization or basic algebra. Gyaan Loop finds the root cause."*

---

### Shot 2: Student Profiles (New vs Returning)
- **Timestamp:** 0:30 – 1:00 (Duration: 30s)
- **Frame:** Student Selector / Profile View.
- **Visual Action:**
  - Click on **Meera (Demo: new learner)** (`demo_learner_new`). Show blank slate: 0 topics attempted, all nodes `unseen`.
  - Click on **Aarav (Demo: prerequisite gaps)** (`demo_learner_gaps`).
  - Cursor hovers over Aarav's starting state badges: `factorization` (Mastery: 25%, Status: Gap) and `linear_equations` (Mastery: 35%, Status: Gap).
- **Audio Cue / Voiceover:**
  - *"Here is Meera, a new student starting from scratch. And here is Aarav, a returning student with prior learning telemetry. Gyaan Loop has already identified two prerequisite gaps in Aarav's profile: linear equations and polynomial factorization."*

---

### Shot 3: The Prerequisite Concept Graph
- **Timestamp:** 1:00 – 1:30 (Duration: 30s)
- **Frame:** Interactive Graph Canvas (React Flow).
- **Visual Action:**
  - Smooth pan across the 13 canonical topics: `integers` $\to$ `algebraic_expressions` $\to$ `polynomials` $\to$ `factorization` $\to$ `solve_by_factorization`.
  - Click on node `solve_by_factorization`.
  - Side panel opens showing details and its two explicit prerequisites: `quadratic_equations` and `factorization`.
- **Audio Cue / Voiceover:**
  - *"Our curriculum is organized as a strict Directed Acyclic Graph with 13 canonical Class 10 math topics. Here we see 'Solving by Factorization', which directly depends on polynomials, linear equations, and factorization."*

---

### Shot 4: Diagnostic Test & Prerequisite Backtrace
- **Timestamp:** 1:30 – 2:15 (Duration: 45s)
- **Frame:** Diagnostic Test View.
- **Visual Action:**
  - Click **Start Diagnostic** on `solve_by_factorization`.
  - Screen displays Question 32: *"Solve $x^2 + 5x + 6 = 0$"*.
  - Cursor hovers over Option A ($x = -2 \text{ or } -3$), then deliberately moves to **Option B: $x = 2 \text{ or } 3$**.
  - Click **Option B**, then click **Submit Answer**.
  - UI displays an amber alert: *"Prerequisite Gap Detected in Factorization!"*.
  - Concept graph animates a backward traversal arrow from `solve_by_factorization` $\to$ `factorization`.
- **Audio Cue / Voiceover:**
  - *"Aarav attempts $x^2 + 5x + 6 = 0$. Like many students, he factorizes $(x+2)(x+3)=0$, but loses the negative signs and answers 2 and 3. Gyaan Loop analyzes the misconception tag and triggers a backtrace directly to polynomial factorization."*

---

### Shot 5: Conversational Lesson & Spoken Teach-Back
- **Timestamp:** 2:15 – 3:00 (Duration: 45s)
- **Frame:** Lesson & Teach-Back Modal.
- **Visual Action:**
  - Click **Open Lesson**.
  - Click the **Listen (Speaker)** button. Audio plays the spoken story aloud:
    *"To solve by factorization, rewrite as two factors multiplied to zero..."*
  - Switch tab to **Teach-Back**.
  - Click **Record (Microphone)** icon.
  - Speak into the mic: *"To solve by factorization, we set $(x+2)(x+3)=0$. By the zero-product rule, either $x+2=0$ giving $x=-2$, or $x+3=0$ giving $x=-3$."*
  - Show real-time interim and final transcript populating the text area.
  - Click **Submit Teach-Back**.
  - Screen displays evaluation card: Score **85%**, Covered Points: *Zero-product rule, sign inversion*.
- **Audio Cue / Voiceover:**
  - *"Gyaan Loop explains the concept through spoken storytelling using the browser's native Web Speech API—with zero API fees. Then, Aarav uses the Feynman technique: he speaks the concept back in his own words. Our AI engine grades his conceptual understanding, praising what he got right and isolating what he missed."*

---

### Shot 6: Smart Flashcards & Spaced Repetition (SM-2)
- **Timestamp:** 3:00 – 3:35 (Duration: 35s)
- **Frame:** Flashcard Review & Spaced Repetition Screen.
- **Visual Action:**
  - Click **Review Flashcards**.
  - Display the generated flashcard: *"Why does $x+2=0 \implies x=-2$?"*.
  - Click **Flip Card** to show the reverse explanation.
  - Click rating button: **Good (Quality 4)**. Card leaves the queue.
  - Click the demo button: **Advance 3 Days**.
  - The review queue instantly refreshes, showing the card due for review.
- **Audio Cue / Voiceover:**
  - *"Flashcards are generated only for Aarav's diagnosed gaps—not a generic 50-card deck. Rating the card triggers our SM-2 spaced repetition scheduler. Using our demo time-advance control, we simulate three days passing: the card is cued up right before memory decay occurs."*

---

### Shot 7: Dashboard Summary & Closing
- **Timestamp:** 3:35 – 4:00 (Duration: 25s)
- **Frame:** Student Dashboard / Mastery Progress.
- **Visual Action:**
  - Return to the Dashboard overview.
  - Point to updated mastery score for `factorization` (moved from 25% to 65%).
  - Smooth fade out on the Gyaan Loop logo.
- **Audio Cue / Voiceover:**
  - *"In under four minutes, Aarav moved from failing a quadratic equation to mastering the underlying factorization principle. Deterministic math safety combined with AI-driven empathy: that is Gyaan Loop. Thank you."*

---

## 3. Fallback Protocols for Video Recording

If recording on a resource-constrained demo laptop:
- **Audio Glitch during Recording:** If system audio capture crackles, record video silently and use a clean external phone microphone to record voiceover, then mux together.
- **Speech API Misfire during Recording:** If Chrome speech recognition takes longer than 2 seconds, utilize the pre-populated editable text field in the teach-back UI and speak over it during playback.
- **Mock Response Option:** Set `AI_MOCK=1` in the backend environment before recording to ensure instant, sub-50ms API responses with zero latency jitter.
