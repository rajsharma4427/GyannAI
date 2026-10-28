# Gyaan Loop — Presentation Slides

**Tagline:** Finding the root cause of every math mistake, closing gaps with voice, and locking in mastery.  
**Track:** AI in Education / Class 10 Mathematics  
**Team:** 4-Person Agile Hackathon Team  

---

## Slide 1: Gyaan Loop — Problem and Vision

### Headline
Transforming Class 10 Math from Rote Memorization into Concept-Rooted Mastery.

### Key Points
- **The Core Problem:** Class 10 board exam mathematics builds on a steep prerequisite ladder (arithmetic → algebra → polynomials → quadratic equations). When students fail a problem, standard tools merely give them a red cross or a robotic answer key.
- **The Vision:** An adaptive AI tutor that acts like an empathetic, expert teacher: finding *why* a student stumbled by walking back through prerequisite concepts, explaining the fix through natural conversational voice, and locking in retention with targeted spaced repetition.
- **Accessible & Zero-Cost:** Designed specifically for Indian learners (English, Hindi, Hinglish) with zero paid speech APIs and lightweight browser-native intelligence.

### Presenter Notes (20s)
> "Good morning judges. Most ed-tech apps today tell a student *that* they are wrong, or feed them the final answer. But in math, a mistake in Class 10 quadratics is almost never about quadratics itself—it is usually a hidden crack in Class 8 factorization or Class 7 negative signs. Gyaan Loop diagnoses the root cause, speaks the concept naturally, and closes the learning loop."

---

## Slide 2: The Real Problem Students Face

### Headline
The "Prerequisite Trap" and the Illusion of Understanding.

### Key Points
- **The Prerequisite Trap:** In a topic like *Solving Quadratic Equations by Factorization*, a student missing $x^2 + 5x + 6 = 0$ might pick $x = 2, 3$ instead of $x = -2, -3$. 
  - Standard grading: "Incorrect. Score: 0/1."
  - Reality: The student understood the quadratic concept, but forgot the zero-product property sign rule in linear equations.
- **One-Size-Fits-All Practice:** Giving 50 identical quadratic drills burns students out without fixing the foundational gap.
- **The Affordability Chasm:** Private 1-on-1 human tutoring provides root-cause diagnosis, but costs ₹500–₹1,500/hour, making it inaccessible to millions of government and tier-2/3 school students.
- **Passive Video Fatigue:** Students watch 20-minute lecture videos passively without ever articulating or proving their conceptual grasp.

### Presenter Notes (25s)
> "When a Class 10 student fails a quadratic equation question, teachers don't have the time to sit and trace whether the error happened at factorization, like-terms collection, or negative signs. Students end up practicing 50 quadratic equations when what they actually needed was 5 minutes on the zero-product property. That is the gap Gyaan Loop bridges."

---

## Slide 3: Our Solution and User Journey

### Headline
The 6-Step Closed Loop: Diagnose → Backtrace → Spoken Story → Teach-Back → Flashcards → Spaced Review.

### Key Points
1. **Set Goal or Load Syllabus:** Start with the standard Class 10 curriculum (13 canonical topics) or input a custom board syllabus.
2. **Diagnostic Evaluation:** Attempt targeted multi-difficulty questions ($D_1 \to D_2 \to D_3$).
3. **Automated Prerequisite Backtrace:** Mistakes trigger an intelligent trace backwards along the directed prerequisite graph to locate the root gap.
4. **Conversational Spoken Lesson:** Listen to an intuitive, jargon-free story/analogy in English, Hindi, or Hinglish.
5. **Active Teach-Back:** The student speaks the concept back in their own words; the system evaluates conceptual coverage and finds missed points.
6. **Smart Spaced Repetition:** Weak points automatically become active flashcards, scheduled dynamically using the SM-2 spaced repetition algorithm.

### Presenter Notes (30s)
> "Here is our closed-loop journey: Aarav takes a diagnostic test. He stumbles on quadratics. Rather than giving up, Gyaan Loop backtraces to factorization, delivers a short spoken story in Hinglish, asks Aarav to explain it back in his own words, and schedules flashcards only for the specific sub-rules he missed. Learning becomes active, conversational, and permanent."

---

## Slide 4: How AI-Powered Learning-Gap Identification Works

### Headline
Combining Deterministic Pedagogical Graphs with Prompted LLM Diagnostics.

### Key Points
- **Directed Acyclic Prerequisite Graph (DAG):**
  - 13 verified canonical topics: `integers` $\to$ `algebraic_expressions` $\to$ `polynomials` $\to$ `factorization` $\to$ `solve_by_factorization`.
  - Mathematically bounded: max backtrace depth of 3 prevents endless disorientation.
- **Where Deterministic Logic Rules:**
  - Graph traversal, difficulty escalation ($D_1 \leftrightarrow D_2 \leftrightarrow D_3$), question serving, and SM-2 review timing are 100% deterministic and repeatable.
- **Where AI Adds Unique Value:**
  - `classify_mistake`: Analyzes the chosen distractor and misconception tags to classify error types (`conceptual`, `procedural`, `careless`, `prerequisite`).
  - `explain_story`: Synthesizes relatable real-world analogies tailored to the student's primary language.
  - `grade_teachback`: Evaluates spoken student transcripts against key conceptual anchors, identifying missing points without strict keyword matching.

### Presenter Notes (30s)
> "Notice how we blend deterministic safety with AI flexibility: we do not let an LLM hallucinate the math syllabus or invent wild dependencies. The curriculum is a strict DAG. But when a student picks a specific distractor, our AI classifier analyzes the error type, isolates the prerequisite, and grades spoken explanations semantically."

---

## Slide 5: Architecture and Technology Stack

### Headline
Four Decoupled Modules, Zero-Cost Client-Side Voice, Robust Shared Contracts.

```
+-------------------------------------------------------------------------------+
|                                  BROWSER (P3)                                 |
|  React 18 + Vite + TypeScript + Tailwind CSS | Zustand State | Web Speech API |
+---------------------------------------+---------------------------------------+
                                        | REST API (HTTP/JSON)
                                        v
+-------------------------------------------------------------------------------+
|                                 BACKEND (P2)                                  |
|     FastAPI (Python 3.11) + Uvicorn | Pydantic v2 Contracts | SQLite (core.db) |
+-------------------+---------------------------------------+-------------------+
                    | Startup Seed                                  | Python SDK
                    v                                               v
+---------------------------------------+   +-----------------------------------+
|             CONTENT (P4)              |   |          AI ENGINE (P1)           |
| JSON Store: 13 Topics, 39+ Questions, |   | Claude API (claude-sonnet-5-5)    |
| Demo Student States, validate.py      |   | SQLite Cache (ai_cache.db)        |
+---------------------------------------+   +-----------------------------------+
```

### Key Highlights
- **Module Independence:** Frontend (P3), Backend & Learning Engine (P2), AI Engine (P1), Voice/Content/Pitch (P4).
- **Zero Financial Cost for Speech:** Built entirely on standard browser Web Speech APIs (`SpeechRecognition` & `SpeechSynthesis`). Zero cloud STT/TTS fees.
- **Repeatable & Fast Demo:** Pre-cached LLM responses and deterministic mock switches (`AI_MOCK=1`, `VITE_MOCK=1`).

### Presenter Notes (25s)
> "Our architecture is clean and strictly unidirectional: the React UI talks only to FastAPI; FastAPI loads verified content from JSON seeds and invokes the AI engine. We use the browser's native Web Speech API—saving hundreds of dollars on third-party voice APIs while maintaining near-zero latency."

---

## Slide 6: A Real Example of Personalized Learning

### Headline
From a Failed Quadratic Equation to a Mastered Factorization Rule in 3 Minutes.

| Step | Student Interaction | System Action | What is Happening Behind the Scenes |
| :--- | :--- | :--- | :--- |
| **1. Diagnostic** | Solves $x^2 + 5x + 6 = 0$. Selects distractor: $x = 2 \text{ or } x = 3$. | Records choice; detects sign error distractor. | `classify_mistake` identifies `prerequisite` gap pointing to `factorization`. |
| **2. Backtrace** | Prompted with prerequisite question on $(x+2)(x+3) = 0$. | Moves diagnostic node from `solve_by_factorization` $\to$ `factorization`. | Graph animates traversal; mastery is decremented for prerequisite. |
| **3. Spoken Lesson** | Clicks "Listen". Hears: *"Think of zero as a black hole..."* | Web Speech TTS renders lesson audio in Hinglish. | No audio files downloaded; browser renders localized text with proper inflection. |
| **4. Teach-Back** | Speaks: *"If two numbers multiply to zero, at least one of them must be zero."* | Web Speech STT transcribes spoken voice in real time. | `grade_teachback` detects key point covered: score 0.85/1.0. |
| **5. Flashcard** | Flips flashcard: *"Why must $x+2=0 \implies x=-2$?"* Rates: Good. | Schedules next review for 3 days later. | SM-2 algorithm updates interval and ease factor in student profile. |

### Presenter Notes (30s)
> "Here is the exact journey in action. Aarav answers 2 and 3 instead of -2 and -3. Gyaan Loop immediately traces back to the zero-product rule, speaks the lesson aloud, listens to Aarav's own explanation, grades his understanding, and creates a tailored flashcard. In 3 minutes, a compounding mistake is permanently resolved."

---

## Slide 7: MVP Demonstration, Feasibility, and Limitations

### Headline
Honest Engineering: What is Implemented, What is Feasible, What We Guard Against.

### What is Fully Implemented Today (MVP)
- Complete 13-topic Class 10 syllabus with zero prerequisite cycles.
- Verified 39-question seed bank with difficulty levels 1, 2, 3 and explicit misconception tags.
- Deterministic demo students (`demo_learner_gaps` with factorization weaknesses & `demo_learner_new`).
- Standalone Python validator verifying schema integrity and DAG properties.
- React hooks for Web Speech recognition and synthesis with fallback support.
- Full backup demonstration plan with timestamped execution steps.

### Known Limitations & Responsible Engineering
- **Browser Speech Variability:** Web Speech API depends on the browser engine (best on desktop Chrome); mobile or non-Chromium browsers fall back to an editable text box.
- **Model Non-Determinism:** LLMs can occasionally vary in wording; mitigated in MVP via prompt conditioning, Pydantic JSON validation, and SQLite caching.
- **Curriculum Scope:** Currently focused on the Class 10 Quadratic Equations cluster (13 topics); easily extensible to Trigonometry, Triangles, and Probability.

### Presenter Notes (25s)
> "We believe in honest engineering. What you see today is a fully verified, contract-compliant MVP. We don't pretend browser speech is identical across every operating system, which is why our UI includes immediate text editing fallbacks. Every question is mathematically verified, and our validator ensures no circular prerequisite dependencies can ever exist."

---

## Slide 8: Impact, Future Improvements, and Conclusion

### Headline
Democratizing High-Quality 1-on-1 Math Mentorship for Every Student.

### Immediate Impact
- **Saves Classroom Time:** Teachers can instantly view a student's diagnostic graph and pinpoint the exact foundational gaps before exams.
- **Removes Math Anxiety:** Conversational, empathetic voice explanations in Hinglish make learning feel like talking to an elder sibling rather than facing an intimidating textbook.
- **Zero Cost Barrier:** Free for any school or student with a web browser.

### The Roadmap Ahead
- **Subject Expansion:** Full Class 9-12 CBSE Science and Math curriculum.
- **Multilingual TTS/STT:** Support for regional Indian languages (Tamil, Telugu, Marathi, Bengali).
- **Offline / Low-Bandwidth Mode:** Localized quantized lightweight SLM running directly in the browser via WebLLM/ONNX.
- **Teacher Dashboard:** Class-wide heatmaps of prerequisite failure points.

### Summary
> **"Gyaan Loop doesn't just grade students—it understands them, talks with them, and walks with them all the way to mastery."**

---
*Thank you! We welcome your questions.*
