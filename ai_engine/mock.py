"""
ai_engine.mock

Mock implementations of the eight AI functions for Gyaan Loop.
Enables offline development, testing, and full integration with Person 2 (FastAPI Backend)
without requiring API keys or network access.
"""

from typing import List, Optional, Union
import re
import uuid

from ai_engine.contracts import (
    Topic,
    Question,
    MistakeAnalysis,
    Lesson,
    TeachBackResult,
    Flashcard,
    CANONICAL_PREREQUISITES,
)


def _get_topic_id(topic: Union[Topic, str]) -> str:
    """Extract topic ID whether topic is a Topic model or a string ID."""
    if isinstance(topic, Topic):
        return topic.id
    return str(topic)


def _get_topic_name(topic: Union[Topic, str]) -> str:
    """Extract readable topic name whether topic is a Topic model or a string ID."""
    if isinstance(topic, Topic):
        return topic.name or topic.id.replace("_", " ").title()
    return str(topic).replace("_", " ").title()


def mock_generate_questions(
    topic: Union[Topic, str], n: int = 5, difficulty: int = 2
) -> list[Question]:
    """Return n deterministic, valid mock questions."""
    if n <= 0:
        raise ValueError("Question count n must be positive.")
    if difficulty not in (1, 2, 3):
        raise ValueError("Difficulty must be 1, 2, or 3.")

    topic_id = _get_topic_id(topic)
    topic_name = _get_topic_name(topic)
    questions: list[Question] = []

    # Math distractor templates and misconception tags
    samples = [
        {
            "stem": f"Solve the standard equation for {topic_name}: x^2 - 5x + 6 = 0.",
            "correct": "x = 2 or x = 3",
            "wrongs": [
                ("x = -2 or x = -3", "sign_error_in_roots"),
                ("x = 1 or x = 6", "misidentified_factors_of_constant"),
                ("x = 5 or x = 6", "confused_sum_and_product_coefficients"),
            ],
        },
        {
            "stem": f"Find the roots for {topic_name}: 2x^2 + 7x + 3 = 0.",
            "correct": "x = -1/2 or x = -3",
            "wrongs": [
                ("x = 1/2 or x = 3", "forgot_to_negate_factored_terms"),
                ("x = -1 or x = -3", "forgot_to_divide_by_leading_coefficient"),
                ("x = -2 or x = -7", "used_coefficients_directly_as_roots"),
            ],
        },
        {
            "stem": f"What is the discriminant for 3x^2 - 4x + 1 = 0 in {topic_name}?",
            "correct": "4",
            "wrongs": [
                ("-4", "subtracted_b_squared_instead_of_4ac"),
                ("28", "added_4ac_instead_of_subtracting"),
                ("16", "calculated_only_b_squared"),
            ],
        },
        {
            "stem": f"For {topic_name}, identify the nature of roots when b^2 - 4ac = 0.",
            "correct": "Two real and equal roots",
            "wrongs": [
                ("Two distinct real roots", "confused_zero_discriminant_with_positive"),
                ("No real roots (imaginary)", "confused_zero_discriminant_with_negative"),
                ("Only one linear root", "forgot_quadratic_always_has_two_roots"),
            ],
        },
    ]

    for i in range(n):
        sample = samples[i % len(samples)]
        correct_pos = i % 4

        options: list[str] = []
        misconception_tags: list[str] = []
        wrong_idx = 0

        for pos in range(4):
            if pos == correct_pos:
                options.append(sample["correct"])
            else:
                wrong_opt, tag = sample["wrongs"][wrong_idx]
                options.append(wrong_opt)
                misconception_tags.append(tag)
                wrong_idx += 1

        q_id = f"{topic_id}_diff{difficulty}_q{i+1}"
        questions.append(
            Question(
                id=q_id,
                topic_id=topic_id,
                stem=sample["stem"],
                options=options,
                correct_index=correct_pos,
                misconception_tags=misconception_tags,
                difficulty=difficulty,
            )
        )

    return questions


def mock_classify_mistake(
    question: Question,
    chosen_index: int,
    topic: Union[Topic, str],
    prereqs: list[Union[Topic, str]],
) -> MistakeAnalysis:
    """Classify mistake based on input according to contract rules."""
    if chosen_index < 0 or chosen_index >= len(question.options):
        raise ValueError(
            f"Chosen index {chosen_index} is out of bounds for options length {len(question.options)}."
        )
    if chosen_index == question.correct_index:
        raise ValueError(
            f"Chosen index {chosen_index} is the correct answer; only incorrect choices can be classified."
        )

    prereq_ids = [_get_topic_id(p) for p in prereqs]

    if prereq_ids:
        # If prerequisites exist, return prerequisite gap with first prereq ID
        first_prereq = prereq_ids[0]
        return MistakeAnalysis(
            gap_type="prerequisite",
            suspected_prereq_id=first_prereq,
            reason=f"The student struggled with prerequisite foundational concept '{first_prereq}' when working with {question.topic_id}.",
        )
    else:
        # If no prerequisites, return conceptual gap
        return MistakeAnalysis(
            gap_type="conceptual",
            suspected_prereq_id=None,
            reason="The student has a conceptual misunderstanding of the core definition and sign conventions.",
        )


def mock_explain_story(
    topic: Union[Topic, str], gap_type: Optional[str] = None, lang: str = "en"
) -> Lesson:
    """Generate a spoken-style story under 120 words, explanation, terms, and 2 exercises."""
    topic_id = _get_topic_id(topic)
    topic_name = _get_topic_name(topic)

    lang_code = lang.lower() if lang else "en"
    if lang_code == "hi":
        story = (
            f"सोचिए आप एक मिठाई की दुकान पर हैं। आपको 12 लड्डू ऐसे डिब्बों में बांटने हैं कि हर पंक्ति और कॉलम बराबर हो। "
            f"यही {topic_name} का खेल है! जब हम सही जोड़े ढूंढते हैं, तो पूरी पहेली आसानी से सुलझ जाती है। "
            f"गणित भी बिल्कुल आपकी पसंदीदा मिठाई के बराबर हिस्से करने जैसा सीधा और सरल है।"
        )
        explanation = (
            f"{topic_name} को समझने के लिए सबसे पहले हमें बीच वाले पद को दो भागों में तोड़ना होता है। "
            f"पहला कदम: पहले और अंतिम पद का गुणनफल ज्ञात करें। "
            f"दूसरा कदम: ऐसे दो अंक खोजें जिनका जोड़ बीच वाले पद के बराबर हो और गुणा अंतिम पद के बराबर हो। "
            f"तीसरा कदम: दोनों कोष्ठकों को शून्य के बराबर रखकर x के मान निकालें।"
        )
    elif lang_code == "hinglish":
        story = (
            f"Imagine karo tum apne doston ke saath cricket match ke runs calculate kar rahe ho. "
            f"Jab total target pata ho aur remaining overs limited hon, tab run-rate balance karna padta hai. "
            f"Bilkul waise hi {topic_name} mein dono sides ko balance karte hain. "
            f"Ek baar basic pattern samajh aa gaya, toh sixer lagana bahut aasan ho jata hai!"
        )
        explanation = (
            f"{topic_name} solve karte waqt hamesha systematic steps follow karo. "
            f"Step 1: Equation ko standard form ax^2 + bx + c = 0 mein likho. "
            f"Step 2: Do aise numbers dhoondo jinka sum 'b' ho aur product 'ac' ho. "
            f"Step 3: Middle term ko split karke common factors bahar nikaalo. "
            f"Step 4: Har linear factor ko zero se equate karo roots nikaalne ke liye."
        )
    else:  # en default
        story = (
            f"Think of packing mangoes into a square gift box. If you arrange them in equal rows and columns, "
            f"finding the unknown side length is exactly what {topic_name} does. "
            f"When you split the total area into neat rectangles, the missing piece clicks right into place. "
            f"Every quadratic problem is just a puzzle waiting for the right rectangular fit."
        )
        explanation = (
            f"To master {topic_name}, keep these core rules in mind. "
            f"First, arrange your equation in standard form where one side equals zero. "
            f"Next, split the middle coefficient into two parts whose product matches the constant term. "
            f"Group the terms in pairs and factor out common expressions carefully. "
            f"Finally, set each factor to zero to obtain your two solutions. Checking each root confirms your work."
        )

    # Word count check: story must be under 120 words
    word_count = len(story.split())
    if word_count > 120:
        story = " ".join(story.split()[:115]) + "."

    key_terms = [
        "Quadratic Equation",
        "Roots",
        "Factorization",
        "Discriminant",
    ]

    exercises = mock_generate_questions(topic_id, 2, 1)

    return Lesson(
        topic_id=topic_id,
        story=story,
        explanation=explanation,
        key_terms=key_terms,
        exercises=exercises,
    )


def mock_grade_teachback(
    topic: Union[Topic, str], transcript: str, key_points: list[str]
) -> TeachBackResult:
    """Deterministically grade teachback against key points using word overlap."""
    if not key_points:
        raise ValueError("Key points list cannot be empty for teachback grading.")

    topic_id = _get_topic_id(topic)
    topic_name = _get_topic_name(topic)
    words = re.findall(r"\w+", transcript.strip().lower())

    if len(words) < 3:
        return TeachBackResult(
            topic_id=topic_id,
            score=0.0,
            covered=[],
            missing=list(key_points),
            errors=[],
            feedback="We could not hear enough explanation. Please try explaining the key ideas again with a bit more detail!",
        )

    transcript_text = " ".join(words)
    covered: list[str] = []
    missing: list[str] = []

    for kp in key_points:
        kp_words = [w for w in re.findall(r"\w+", kp.lower()) if len(w) > 3]
        if any(w in transcript_text for w in kp_words):
            covered.append(kp)
        else:
            missing.append(kp)

    errors: list[str] = []
    # Formula: fraction covered - 0.1 * errors, clamped [0.0, 1.0]
    raw_score = (len(covered) / len(key_points)) - (0.1 * len(errors))
    score = max(0.0, min(1.0, round(raw_score, 2)))

    if score >= 0.7:
        feedback = (
            f"Great explanation of {topic_name}! You clearly understood {len(covered)} key concept(s). "
            f"To get full mastery, make sure to also review: {missing[0] if missing else 'advanced practice problems'}."
        )
    else:
        feedback = (
            f"Good effort trying to explain {topic_name}! You mentioned {len(covered)} concept(s) correctly. "
            f"Next, focus specifically on: {missing[0] if missing else 'the definition'} to strengthen your understanding."
        )

    return TeachBackResult(
        topic_id=topic_id,
        score=score,
        covered=covered,
        missing=missing,
        errors=errors,
        feedback=feedback,
    )


def mock_make_flashcards(
    topic: Union[Topic, str],
    gap_type: Optional[str] = None,
    missing: Optional[list[str]] = None,
    n: int = 2,
) -> list[Flashcard]:
    """Generate n mock flashcards."""
    if n <= 0:
        raise ValueError("Flashcard count n must be positive.")

    topic_id = _get_topic_id(topic)
    topic_name = _get_topic_name(topic)
    cards: list[Flashcard] = []
    missing_list = missing or []

    if missing_list:
        source = "teachback"
        for i in range(n):
            target_pt = missing_list[i % len(missing_list)]
            cards.append(
                Flashcard(
                    id=f"{topic_id}_card_{uuid.uuid4().hex[:6]}",
                    topic_id=topic_id,
                    front=f"How do you apply '{target_pt}' in {topic_name}?",
                    back=f"Remember that in {topic_name}, applying '{target_pt.rstrip('.')}' ensures correct mathematical balance.",
                    source=source,
                )
            )
    else:
        source = "gap"
        core_qa = [
            (
                f"What is the standard form of {topic_name}?",
                "The standard form is ax^2 + bx + c = 0 where leading coefficient a is not zero.",
            ),
            (
                f"How do you determine the nature of roots in {topic_name}?",
                "Calculate discriminant D = b^2 - 4ac. Positive means two real roots, zero means one repeated, negative means no real roots.",
            ),
            (
                "What is the zero product property?",
                "If A times B equals 0, then either A = 0, B = 0, or both equal 0.",
            ),
        ]
        for i in range(n):
            q, a = core_qa[i % len(core_qa)]
            cards.append(
                Flashcard(
                    id=f"{topic_id}_card_{uuid.uuid4().hex[:6]}",
                    topic_id=topic_id,
                    front=q,
                    back=a,
                    source=source,
                )
            )

    return cards


def mock_make_note(
    topic: Union[Topic, str], summary: str, lang: str = "en"
) -> str:
    """Generate a 2-4 sentence note under 80 words without markdown headings."""
    topic_name = _get_topic_name(topic)
    lang_code = lang.lower() if lang else "en"

    if lang_code == "hi":
        return (
            f"{topic_name} में मुख्य बात यह है कि समीकरण को हमेशा मानक रूप में व्यवस्थित करें। "
            f"गुणनखंड करते समय मध्य पद के सही टुकड़े पहचानें। "
            f"दोनों उत्तरों को मूल समीकरण में रखकर जांचना न भूलें।"
        )
    elif lang_code == "hinglish":
        return (
            f"{topic_name} solve karte waqt equation ko pehle standard form mein likho. "
            f"Middle term ko split karte samay signs ka dhyan rakhein. "
            f"Final roots ko verify karna ek best habit hai."
        )
    else:
        return (
            f"For {topic_name}, always arrange terms in standard quadratic form before starting. "
            f"Split the middle term by finding numbers whose product equals the product of leading and constant terms. "
            f"Check both roots back in the original equation to ensure complete accuracy."
        )


def mock_extract_syllabus(text: str) -> list[Topic]:
    """Return the 13 canonical Class 10 quadratic track topics with multi-sentence descriptions."""
    canonical_data = [
        ("integers", "Integers and Number Line", "Integers are positive and negative whole numbers including zero. They form the basis for sign rules in algebraic arithmetic. Mastering sign operations prevents sign slips."),
        ("fractions", "Fractions and Decimals", "Fractions represent parts of a whole using numerator and denominator. They are essential for manipulating rational coefficients. Cross-multiplication simplifies fractional equations."),
        ("algebraic_expressions", "Algebraic Expressions", "Expressions combine variables, constants, and operators without an equality sign. Like terms can be grouped and combined. Expanding brackets follows distributive laws."),
        ("linear_equations", "Linear Equations", "Linear equations equate degree-one expressions to find an unknown variable. Isolating the variable requires inverse arithmetic operations. Both sides must remain balanced."),
        ("exponents", "Exponents and Powers", "Exponents indicate repeated multiplication of a base by itself. The product and power rules simplify complex terms. Zero and negative exponents follow consistent conventions."),
        ("polynomials", "Polynomials", "Polynomials are algebraic expressions with non-negative integer powers. The degree indicates the highest exponent present. Polynomial addition and subtraction align like powers."),
        ("factorization", "Factorization of Polynomials", "Factorization rewrites a polynomial as a product of simpler factors. Finding common monomials is always the initial step. Grouping terms helps factor four-term expressions."),
        ("identities", "Algebraic Identities", "Algebraic identities are equalities that hold true for every value. Key identities include perfect squares and differences of squares. Recognizing identity patterns speeds up factoring."),
        ("square_roots", "Square Roots and Radicals", "A square root yields the value that produces the original number when squared. Positive numbers possess both positive and negative roots. Radical expressions can be simplified by factoring squares."),
        ("quadratic_equations", "Quadratic Equations", "A quadratic equation has degree two and standard form ax squared plus bx plus c equals zero. The coefficient a cannot equal zero. Solutions are termed roots or zeros."),
        ("solve_by_factorization", "Solving Quadratics by Factorization", "Solving by factoring sets the standard form quadratic equal to zero. Splitting the middle term creates binomial factors. The zero product property reveals the roots."),
        ("discriminant", "Discriminant and Nature of Roots", "The discriminant is b squared minus 4ac found under the radical. Positive discriminant indicates two distinct real roots. Zero indicates repeated roots and negative indicates non-real roots."),
        ("quadratic_formula", "The Quadratic Formula", "The quadratic formula calculates roots directly using coefficients a, b, and c. It works for every quadratic equation regardless of factorability. The plus-minus symbol provides two potential roots."),
    ]

    topics: list[Topic] = []
    for tid, name, desc in canonical_data:
        topics.append(
            Topic(
                id=tid,
                name=name,
                description=desc,
                prereq_ids=CANONICAL_PREREQUISITES.get(tid, []),
                parent_id=None,
            )
        )
    return topics


def mock_draft_syllabus(goal: str) -> list[Topic]:
    """Draft a valid curriculum track derived from the learning goal."""
    # When goal pertains to Class 10, math, boards, or quadratic equations, reuse the 13 canonical topics
    clean_goal = goal.strip().lower()
    if any(k in clean_goal for k in ("class", "10", "math", "quadratic", "board", "prep", "exam", "algebra")):
        return mock_extract_syllabus(goal)

    # For other arbitrary goals, generate an ordered 5-topic track
    clean_title = goal.strip().replace('"', '')
    track_defs = [
        ("foundations", f"Foundations of {clean_title}", f"Core terminology and basic concepts for {clean_title}. Essential arithmetic and definitions needed to start."),
        ("fundamentals", f"Fundamental Operations in {clean_title}", f"Primary operations and standard techniques. Step-by-step procedures for simple problems."),
        ("intermediate_methods", f"Intermediate Methods for {clean_title}", f"Combining multiple operations into structured solutions. Recognizing patterns and avoiding pitfalls."),
        ("advanced_applications", f"Advanced Applications of {clean_title}", f"Complex scenarios and real-world word problems. Choosing the most efficient method for complex cases."),
        ("mastery_review", f"Mastery Review and Assessment in {clean_title}", f"Comprehensive review across all problem types. Verification strategies to confirm correct answers."),
    ]

    topics: list[Topic] = []
    prev_id: list[str] = []
    for tid, name, desc in track_defs:
        topics.append(
            Topic(
                id=tid,
                name=name,
                description=desc,
                prereq_ids=list(prev_id),
                parent_id=None,
            )
        )
        prev_id = [tid]

    return topics
