import type { DemoProfile, Flashcard, Lesson, Note, TopicState } from '../api/types';
import { TOPICS } from './topics';
import { QUESTIONS_BY_TOPIC } from './questions';

export const DEMO_PROFILES: DemoProfile[] = [
  { student_id: 'demo_learner_gaps', name: 'Aarav Sharma', description: 'Returning learner · practice history included', kind: 'returning' },
  { student_id: 'demo_learner_new', name: 'Meera Verma', description: 'New learner · no learning history yet', kind: 'new' },
  { student_id: 'demo-aarav', name: 'Aarav (demo-aarav)', description: 'Returning learner · alias', kind: 'returning' },
  { student_id: 'demo-new', name: 'Meera (demo-new)', description: 'New learner · alias', kind: 'new' },
];

const state = (topic_id: string, mastery: number, status: TopicState['status'], gap_type: TopicState['gap_type'] = null, interval_days = 0): TopicState => ({
  topic_id, mastery, confidence: status === 'mastered' ? 0.84 : status === 'gap' ? 0.38 : status === 'learning' ? 0.6 : 0.1,
  gap_type, interval_days, ease: 2.5, next_review: status === 'gap' || status === 'learning' ? '2026-10-28' : null, status,
});

export const RETURNING_STATES: TopicState[] = [
  state('integers', 0.92, 'mastered'), state('fractions', 0.78, 'learning'),
  state('algebraic_expressions', 0.82, 'mastered'), state('linear_equations', 0.34, 'gap', 'procedural'),
  state('exponents', 0.74, 'learning'), state('polynomials', 0.51, 'learning'),
  state('factorization', 0.28, 'gap', 'prerequisite'), state('identities', 0.64, 'learning'),
  state('square_roots', 0.62, 'learning'), state('quadratic_equations', 0.46, 'learning'),
  state('solve_by_factorization', 0.31, 'gap', 'prerequisite'), state('quadratic_formula', 0.22, 'gap', 'conceptual'),
  state('discriminant', 0, 'unseen'),
];
export const NEW_STATES: TopicState[] = TOPICS.map((topic) => state(topic.id, 0, 'unseen'));

export const SEED_NOTES: Note[] = [
  { id: 'note-fac-1', topic_id: 'factorization', author: 'ai', body: 'Look for two numbers that multiply to the constant term and add to the middle coefficient.', created_at: '2026-10-27T10:00:00Z' },
  { id: 'note-lin-1', topic_id: 'linear_equations', author: 'student', body: 'Remember: whatever I do to one side, I do to the other side too.', created_at: '2026-10-26T16:30:00Z' },
  { id: 'note-quad-1', topic_id: 'quadratic_equations', author: 'ai', body: 'Standard form: ax² + bx + c = 0, where a ≠ 0.', created_at: '2026-10-27T10:05:00Z' },
];

export const SEED_FLASHCARDS: Flashcard[] = [
  { id: 'card-1', topic_id: 'factorization', front: 'What two conditions help factor x² + bx + c?', back: 'Find two numbers whose product is c and whose sum is b.', source: 'gap' },
  { id: 'card-2', topic_id: 'factorization', front: 'Factorize x² − 9.', back: '(x − 3)(x + 3) — it is a difference of squares.', source: 'gap' },
  { id: 'card-3', topic_id: 'linear_equations', front: 'What keeps a linear equation balanced?', back: 'Perform the same operation on both sides of the equation.', source: 'teachback' },
  { id: 'card-4', topic_id: 'quadratic_equations', front: 'What is the standard form of a quadratic equation?', back: 'ax² + bx + c = 0, with a ≠ 0.', source: 'gap' },
];

const englishLessons: Record<string, Omit<Lesson, 'topic_id'>> = {
  factorization: {
    story: 'Think of an expression as a box. Factorization is opening that box and finding the smaller pieces that multiply to make the original expression.',
    explanation: 'To factor x² + 5x + 6, look for two numbers whose product is 6 and whose sum is 5. Those numbers are 2 and 3, so x² + 5x + 6 = (x + 2)(x + 3). Check by multiplying the factors back together.',
    key_terms: ['factor', 'product', 'coefficient', 'constant term'], exercises: QUESTIONS_BY_TOPIC.factorization,
  },
  linear_equations: {
    story: 'An equation is like a balanced weighing scale. To keep it balanced, make the same change on both sides.',
    explanation: 'For 2x + 4 = 14, subtract 4 from both sides to get 2x = 10. Divide both sides by 2, so x = 5. Substitute 5 back into the original equation to check it.',
    key_terms: ['variable', 'coefficient', 'inverse operation', 'solution'], exercises: QUESTIONS_BY_TOPIC.linear_equations,
  },
  quadratic_equations: {
    story: 'A quadratic equation has an x-squared term. Before choosing a solving method, first put every term on one side so the other side is zero.',
    explanation: 'The standard form is ax² + bx + c = 0, with a not equal to zero. For x² − 5x + 6 = 0, the coefficients are a = 1, b = −5, and c = 6. Because it factors into (x − 2)(x − 3), the roots are 2 and 3.',
    key_terms: ['quadratic', 'standard form', 'coefficient', 'root'], exercises: QUESTIONS_BY_TOPIC.quadratic_equations,
  },
  solve_by_factorization: {
    story: 'Once a quadratic is written as two factors, the zero-product rule says at least one factor must be zero.',
    explanation: 'Solve x² − 5x + 6 = 0 by factoring it into (x − 2)(x − 3) = 0. Set each factor equal to zero: x − 2 = 0 or x − 3 = 0. Therefore, x = 2 or x = 3.',
    key_terms: ['zero-product rule', 'factor pair', 'root'], exercises: QUESTIONS_BY_TOPIC.solve_by_factorization,
  },
  quadratic_formula: {
    story: 'When a quadratic does not factor neatly, the quadratic formula gives a reliable route to its roots.',
    explanation: 'For ax² + bx + c = 0, use x = (−b ± √(b² − 4ac)) / 2a. Identify a, b and c carefully, calculate the discriminant first, then substitute into the formula.',
    key_terms: ['quadratic formula', 'discriminant', '±', 'root'], exercises: QUESTIONS_BY_TOPIC.quadratic_formula,
  },
  discriminant: {
    story: 'The discriminant is a quick signal: before calculating the roots, it tells you how many real roots to expect.',
    explanation: 'Calculate D = b² − 4ac. If D is positive, there are two distinct real roots; if D is zero, there is one repeated real root; if D is negative, there are no real roots.',
    key_terms: ['discriminant', 'real roots', 'repeated root'], exercises: QUESTIONS_BY_TOPIC.discriminant,
  },
};

const languageLessons: Partial<Record<string, Partial<Record<'hi' | 'hinglish', { story: string; explanation: string }>>>> = {
  factorization: {
    hi: { story: 'किसी व्यंजक को एक डिब्बे की तरह सोचिए। गुणनखंड करना यानी उस डिब्बे को खोलकर ऐसे छोटे भाग ढूँढना जिनका गुणनफल मूल व्यंजक बने।', explanation: 'x² + 5x + 6 के लिए दो संख्याएँ ढूँढें जिनका गुणनफल 6 और योग 5 हो। ये संख्याएँ 2 और 3 हैं, इसलिए x² + 5x + 6 = (x + 2)(x + 3)।' },
    hinglish: { story: 'Expression ko ek box ki tarah socho. Factorization matlab box ko kholkar aise chhote parts dhoondhna jinka product original expression banaye.', explanation: 'x² + 5x + 6 ke liye do numbers chahiye jinka product 6 aur sum 5 ho. Numbers 2 aur 3 hain, isliye factorization (x + 2)(x + 3) hai.' },
  },
  quadratic_equations: {
    hi: { story: 'Quadratic equation में x का square वाला term होता है। हल करने का तरीका चुनने से पहले सभी terms को एक तरफ लाएँ और दूसरी तरफ zero रखें।', explanation: 'Standard form ax² + bx + c = 0 होती है, जहाँ a शून्य नहीं होता। x² − 5x + 6 = 0 में a = 1, b = −5 और c = 6 हैं। इसके roots 2 और 3 हैं।' },
    hinglish: { story: 'Quadratic equation mein x-square term hota hai. Solve karne ka method choose karne se pehle sab terms ko ek side lao aur doosri side zero rakho.', explanation: 'Standard form ax² + bx + c = 0 hoti hai, jahan a zero nahi hota. x² − 5x + 6 = 0 mein a = 1, b = −5 aur c = 6 hain. Iske roots 2 aur 3 hain.' },
  },
};

export function getLesson(topicId: string, lang: 'en' | 'hi' | 'hinglish'): Lesson {
  const topic = TOPICS.find((item) => item.id === topicId) ?? TOPICS[0];
  const base = englishLessons[topicId] ?? {
    story: `${topic.name} is a building block. Learn the core idea, work through an example, and then try a question without looking at the answer.`,
    explanation: `${topic.description} Start by identifying what is known, choose the rule that applies, and check your result against the original question.`,
    key_terms: [topic.name.toLowerCase(), 'worked example', 'practice'],
    exercises: QUESTIONS_BY_TOPIC[topicId] ?? QUESTIONS_BY_TOPIC.integers,
  };
  const translated = lang === 'en' ? undefined : languageLessons[topicId]?.[lang];
  return { topic_id: topicId, ...base, ...(translated ? { story: translated.story, explanation: translated.explanation } : {}) };
}
