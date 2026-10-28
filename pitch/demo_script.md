# Gyaan Loop — 4-Minute Live Demonstration Script

**Total Time Budget:** Exactly 4 Minutes (240 Seconds)  
**Presenter:** Lead Presenter / Person 4  
**Backup Driver:** Teammate with keyboard/mouse navigation  
**Environment:** Desktop Google Chrome on `http://localhost:5173` (Backend on `http://localhost:8000`)

---

## Time Budget Breakdown

| Section | Timestamp | Duration | Focus Area |
| :--- | :--- | :--- | :--- |
| **1. Hook & Target User** | 0:00 – 0:30 | 30s | The core problem, target student profile, and thesis |
| **2. New Student vs Returning Student** | 0:30 – 1:00 | 30s | Loading demo profiles (`demo_learner_new` vs `demo_learner_gaps`) |
| **3. The Concept Graph & Prerequisite Tree** | 1:00 – 1:30 | 30s | Visualizing the 13-node Class 10 math syllabus |
| **4. Diagnostic & Intentional Failure** | 1:30 – 2:15 | 45s | Triggering backtrace from `solve_by_factorization` to `factorization` |
| **5. Spoken Lesson & Active Teach-Back** | 2:15 – 3:00 | 45s | Browser Web Speech TTS listen & STT voice explanation |
| **6. Flashcards, Notes & Spaced Repetition** | 3:00 – 3:35 | 35s | SM-2 review scheduling and date-advance demo |
| **7. AI vs Deterministic Architecture & Close** | 3:35 – 4:00 | 25s | Honest architecture breakdown, zero-cost feasibility, closing |

---

## Minute-by-Minute Walkthrough

### Part 1: Hook & Target User (0:00 – 0:30 | 30 Seconds)

**Visual:** Presenter stands beside laptop screen showing Gyaan Loop home screen.

**Action:**
- Display the clean, modern Gyaan Loop landing page with student selection.

**Spoken Dialogue:**
> *"Judges, meet Aarav and Meera. They are Class 10 students preparing for their board exams. In India, over 25 million students take board exams every year, and math anxiety is their biggest roadblock.*
>
> *When a student solves a quadratic equation and gets it wrong, almost every existing ed-tech app simply shows a red 'X' and displays the formula. But math is a ladder: a failure at Class 10 quadratics is almost always caused by an unaddressed gap in Class 8 factorization or sign rules.*
>
> *Gyaan Loop is an AI tutor that finds the root cause of every math mistake, explains it in spoken conversational language, and locks in mastery through active teach-back and spaced repetition."*

---

### Part 2: New Student vs Returning Student (0:30 – 1:00 | 30 Seconds)

**Visual:** Student profile selector.

**Action:**
1. Click on **Meera (Demo: new learner)**. Show that her graph is clean, with all 13 topics in the `unseen` state.
2. Switch to **Aarav (Demo: prerequisite gaps)** (`student_id: demo_learner_gaps`).
3. Point to the topic status chips on the screen.

**Spoken Dialogue:**
> *"Let's look at how Gyaan Loop personalizes learning. For a brand new student like Meera, all topics start fresh in an 'unseen' state. She can start an introductory diagnostic or set a custom goal.*
>
> *Now let's switch to Aarav, a returning student. Notice his learning history: the system has already flagged two specific weaknesses: `linear_equations` with a conceptual gap, and `factorization` with a procedural gap at only 25% mastery.*
>
> *Because Gyaan Loop remembers each student's prerequisite health, it tailors every question and explanation to their individual history."*

---

### Part 3: The Concept Graph & Prerequisite Tree (1:00 – 1:30 | 30 Seconds)

**Visual:** Interactive Concept Graph / React Flow DAG.

**Action:**
1. Navigate to the **Concept Graph** tab.
2. Hover over `integers` $\to$ `algebraic_expressions` $\to$ `polynomials` $\to$ `quadratic_equations`.
3. Click on the node **Solving by factorization** (`solve_by_factorization`). Show its prerequisites: `quadratic_equations` and `factorization`.

**Spoken Dialogue:**
> *"Here is our Class 10 Mathematics Prerequisite Graph. It contains 13 canonical topics, rigorously organized as a Directed Acyclic Graph—verified by our automated content validator to ensure zero circular dependencies.*
>
> *Notice that `solve_by_factorization` doesn't exist in a vacuum. It explicitly depends on both standard quadratic equations and polynomial factorization. Now let's watch what happens when Aarav attempts to solve problems in this topic."*

---

### Part 4: Diagnostic & Intentional Failure (1:30 – 2:15 | 45 Seconds)

**Visual:** Diagnostic screen showing Question 32 (`solve_by_factorization_d2`).

**Action:**
1. Click **Start Diagnostic** on `solve_by_factorization`.
2. The question appears on screen:  
   **"Solve $x^2 + 5x + 6 = 0$."**
   - Option A: $x = -2 \text{ or } x = -3$ *(Correct)*
   - Option B: $x = 2 \text{ or } x = 3$ *(Plausible sign-reversal distractor)*
   - Option C: $x = -1 \text{ or } x = -6$
   - Option D: $x = 2 \text{ or } x = -3$
3. Deliberately click **Option B: $x = 2 \text{ or } x = 3$** and click **Submit Answer**.
4. Observe the screen: the backend calls `classify_mistake`. The UI immediately alerts: **"Prerequisite gap detected in Factorization!"** and animates a backtrace step on the graph.

**Spoken Dialogue:**
> *"Aarav sees: $x^2 + 5x + 6 = 0$. Like thousands of students, he factorizes $(x+2)(x+3) = 0$, but when solving for $x$, he loses the negative signs and picks $x = 2 \text{ or } 3$.*
>
> *Watch the system response: instead of just saying 'wrong', Gyaan Loop analyzes the distractor tag: 'lose signs when setting factors to zero'. The AI engine detects this is a prerequisite breakdown, and our backtrace engine immediately steps back along the graph into `factorization` to fix the foundational crack!"*

---

### Part 5: Spoken Lesson & Active Teach-Back (2:15 – 3:00 | 45 Seconds)

**Visual:** Lesson & Teach-Back Modal.

**Action:**
1. Click **Open Lesson**.
2. Click the **Listen** button (Speaker icon). Web Speech synthesis speaks the short lesson aloud in English/Hinglish:  
   *"To solve a quadratic equation by factoring, rewrite it as two factors multiplied together that equal zero. By the zero-product rule, if $A \times B = 0$, then $A = 0$ or $B = 0$..."*
3. Switch to the **Teach-Back** tab.
4. Click the **Microphone** icon. Speak into the microphone:  
   *"To solve by factorization, we write $(x+2)(x+3) = 0$. If two numbers multiply to zero, one of them must be zero, so $x+2=0$ gives $x=-2$, and $x+3=0$ gives $x=-3$."*
5. Show the real-time interim and final transcript streaming directly onto the screen.
6. Click **Submit Teach-Back**.
7. The evaluation returns: Score **85%**, points covered: *Zero-product property, sign inversion*, encouraging feedback generated.

**Spoken Dialogue:**
> *"Students learn best when they hear concepts conversationally and explain them back aloud. Using the browser's native Web Speech API—with zero third-party API costs—Gyaan Loop reads the lesson story aloud.*
>
> *Then comes the Feynman technique: active Teach-Back. Aarav clicks the mic and speaks his understanding in his own words. Our speech hook captures the speech in real-time, and the AI engine grades his explanation against the core concepts, praising what he understood and highlighting what he missed."*

---

### Part 6: Flashcards, Notes & Spaced Repetition (3:00 – 3:35 | 35 Seconds)

**Visual:** Review Queue / Spaced Repetition Screen.

**Action:**
1. Click **Review Flashcards**.
2. Show the newly generated card:  
   - **Front:** *"When $(x+2)(x+3)=0$, why is $x=-2$ and not $+2$?"*
   - Click **Flip Card**.
   - **Back:** *"Because $x+2=0 \implies x = 0 - 2 = -2$. Subtracting 2 from both sides changes the sign."*
3. Click rating **Good (Quality 4)**. Card disappears from queue; next review scheduled in 3 days.
4. Click **Advance 3 Days** (Demo developer control).
5. The review queue immediately updates showing the card is due for review again!

**Spoken Dialogue:**
> *"Gyaan Loop doesn't flood students with hundreds of generic flashcards. It generates targeted cards only for the exact gaps identified during the diagnostic and teach-back.*
>
> *When Aarav reviews this card and rates it 'Good', our SM-2 algorithm schedules his next review. Notice our demo accelerator: clicking 'Advance 3 Days' simulates time passing, proving that spaced repetition dynamically brings back concepts before they fade from memory."*

---

### Part 7: AI vs Deterministic Architecture & Close (3:35 – 4:00 | 25 Seconds)

**Visual:** Architecture slide / Dashboard summary.

**Action:**
- Return to the Dashboard showing overall mastery improvement and streak counter.

**Spoken Dialogue:**
> *"Let us be transparent about how this works: our prerequisite graph traversal, question bank, and SM-2 scheduling are 100% deterministic, mathematically verified, and zero-hallucination. AI is applied where it shines: classifying error patterns, narrating conversational lessons, and semantically grading spoken teach-backs.*
>
> *With zero external voice fees, lightweight local caching, and offline resilience, Gyaan Loop puts an expert 1-on-1 math tutor into the hands of every student who needs one. Thank you!"*

---

## Live Demo Recovery & Fallback Protocol

If anything unexpected occurs during the live presentation, use these seamless fallbacks without pausing:

1. **If Microphone is Denied or Speech Recognition Fails:**
   - *Presenter action:* Do not struggle with browser permissions.
   - *What to say:* *"Because browser microphone permissions vary across environments, our hook includes a graceful text fallback."*
   - *Click:* Paste the pre-written sentence into the transcript box and click Submit.
2. **If Speech Synthesis (Audio Output) is Inaudible in the Venue:**
   - *Presenter action:* Click Cancel.
   - *What to say:* *"In a loud auditorium, students can also read the bite-sized story directly on screen."*
   - Read the first 2 sentences aloud yourself.
3. **If Wi-Fi Drops or Anthropic API Key Fails:**
   - *Presenter action:* Ensure backend was started with `AI_MOCK=1`.
   - *What to say:* *"We designed Gyaan Loop with an offline cache and deterministic mock engine so students can continue learning even with intermittent rural connectivity."*
   - The diagnostic backtrace, lesson, teach-back grade, and flashcards will return pre-warmed valid contract responses instantly.
4. **If Returning Student Profile is Not Pre-selected:**
   - Select `demo_learner_gaps` from the dropdown, or directly navigate to `solve_by_factorization`.
