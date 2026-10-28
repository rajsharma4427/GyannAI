import type {
  AdvanceDaysRequest, AdvanceDaysResponse, DashboardResponse, DiagnosticAnswerRequest,
  DiagnosticAnswerResponse, DiagnosticStartRequest, DiagnosticStartResponse, Flashcard,
  FlashcardReviewRequest, FlashcardReviewResponse, FlashcardsResponse, GraphResponse, Lang,
  Lesson, Note, NoteCreateRequest, NotesResponse, SyllabusRequest, SyllabusResponse,
  TeachBackRequest, TeachBackResponse, Topic, TopicState, StudentCreateRequest, StudentCreateResponse,
} from './types';
import { DEMO_PROFILES, NEW_STATES, RETURNING_STATES, SEED_FLASHCARDS, SEED_NOTES, getLesson } from '../data/demo';
import { QUESTIONS_BY_TOPIC, QUESTIONS_BY_ID } from '../data/questions';
import { TOPICS, TOPIC_BY_ID } from '../data/topics';

interface MockSession { student_id: string; topic_id: string; step: number; question_id: string; }
const sessions = new Map<string, MockSession>();
const stateOverrides = new Map<string, TopicState[]>();
const customProfiles = new Map<string, { name: string; lang: Lang }>();
const reviewedCards = new Set<string>();
const generatedCards = new Map<string, Flashcard[]>();
const noteOverrides = new Map<string, Note[]>();
let dayOffset = 0;

function hydrateCustomProfile(studentId: string) {
  if (customProfiles.has(studentId) || typeof localStorage === 'undefined') return;
  try {
    const stored = JSON.parse(localStorage.getItem('gyaan-loop-custom-profiles') || '{}') as Record<string, { name: string; lang: Lang }>;
    if (stored[studentId]) customProfiles.set(studentId, stored[studentId]);
  } catch { /* custom demo profile metadata is optional */ }
}
function persistCustomProfiles() {
  try { localStorage.setItem('gyaan-loop-custom-profiles', JSON.stringify(Object.fromEntries(customProfiles))); } catch { /* localStorage may be disabled */ }
}
function isNewLearner(studentId: string): boolean {
  return studentId === 'demo-new' || studentId === 'demo_learner_new' || customProfiles.has(studentId);
}
function copyStates(studentId: string): TopicState[] {
  hydrateCustomProfile(studentId);
  const cached = stateOverrides.get(studentId);
  if (cached) return cached;
  const source = isNewLearner(studentId) ? NEW_STATES : RETURNING_STATES;
  const cloned = source.map((item) => ({ ...item }));
  stateOverrides.set(studentId, cloned);
  return cloned;
}
function updateState(studentId: string, topicId: string, patch: Partial<TopicState>) {
  const states = copyStates(studentId);
  const found = states.find((item) => item.topic_id === topicId);
  if (found) Object.assign(found, patch);
}
function cloneTopics(): Topic[] { return TOPICS.map((topic) => ({ ...topic, prereq_ids: [...topic.prereq_ids] })); }
function profileName(studentId: string): string {
  hydrateCustomProfile(studentId);
  return DEMO_PROFILES.find((profile) => profile.student_id === studentId)?.name ?? customProfiles.get(studentId)?.name ?? 'Learner';
}
function currentDate(daysAhead = 0): string {
  const date = new Date('2026-10-28T12:00:00Z');
  date.setUTCDate(date.getUTCDate() + dayOffset + daysAhead);
  return date.toISOString().slice(0, 10);
}
function cardsFor(studentId: string): Flashcard[] {
  hydrateCustomProfile(studentId);
  const seedCards = isNewLearner(studentId) ? [] : SEED_FLASHCARDS;
  const ownGenerated = generatedCards.get(studentId) ?? [];
  return [...seedCards, ...ownGenerated].filter((card) => !reviewedCards.has(`${studentId}:${card.id}`)).map((card) => ({ ...card }));
}

export async function mockCreateStudent(request: StudentCreateRequest): Promise<StudentCreateResponse> {
  const student_id = `demo-custom-${Date.now().toString(36)}`;
  customProfiles.set(student_id, { name: request.name.trim() || 'Learner', lang: request.lang });
  persistCustomProfiles();
  stateOverrides.set(student_id, NEW_STATES.map((item) => ({ ...item })));
  return { student_id };
}
export async function mockCreateSyllabus(request: SyllabusRequest): Promise<SyllabusResponse> {
  // The demo syllabus is intentionally fixed to the shared, validated 13-topic graph.
  if (!request.text?.trim() && !request.goal?.trim()) throw new Error('Add syllabus text or a learning goal to continue.');
  return { topics: cloneTopics() };
}
export async function mockGetGraph(studentId: string): Promise<GraphResponse> {
  return { topics: cloneTopics(), states: copyStates(studentId).map((item) => ({ ...item })) };
}
export async function mockStartDiagnostic(request: DiagnosticStartRequest): Promise<DiagnosticStartResponse> {
  const topicId = TOPIC_BY_ID[request.topic_id] ? request.topic_id : 'solve_by_factorization';
  const first = (QUESTIONS_BY_TOPIC[topicId] ?? QUESTIONS_BY_TOPIC.solve_by_factorization)[0];
  const session_id = `session-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
  sessions.set(session_id, { student_id: request.student_id, topic_id: topicId, step: 0, question_id: first.id });
  return { session_id, question: { ...first, options: [...first.options] } };
}
export async function mockAnswerDiagnostic(request: DiagnosticAnswerRequest): Promise<DiagnosticAnswerResponse> {
  const session = sessions.get(request.session_id);
  if (!session) throw new Error('This practice session has expired. Start a new diagnostic.');
  const question = QUESTIONS_BY_ID[request.question_id];
  if (!question) throw new Error('Question not found in the demo seed bank.');
  const correct = question.correct_index === request.chosen_index;
  const oldState = copyStates(session.student_id).find((item) => item.topic_id === question.topic_id);
  const previous = oldState?.mastery ?? 0;
  const mastery = Math.max(0, Math.min(1, correct ? previous + (1 - previous) * 0.3 : previous * 0.6));
  updateState(session.student_id, question.topic_id, {
    mastery,
    status: mastery < 0.4 ? 'gap' : mastery > 0.8 ? 'mastered' : 'learning',
    gap_type: correct ? null : 'prerequisite',
    confidence: Math.min(0.95, (oldState?.confidence ?? 0.3) + 0.08),
    next_review: correct ? currentDate() : currentDate(),
  });

  // The deterministic demo path intentionally shows the agreed root-cause story.
  if (session.step === 0 && !correct && (session.topic_id === 'solve_by_factorization' || session.topic_id === 'quadratic_equations')) {
    const next = QUESTIONS_BY_TOPIC.factorization[1];
    session.step = 1;
    session.question_id = next.id;
    session.topic_id = 'factorization';
    return {
      correct: false, done: false,
      next_question: { ...next, options: [...next.options] },
      backtrace: {
        from_topic_id: question.topic_id,
        to_topic_id: 'factorization',
        reason: 'This step depends on recognising factor pairs. Let’s check that prerequisite before moving on.',
      },
    };
  }
  if (session.step < 2) {
    const targetTopic = session.topic_id;
    const candidates = QUESTIONS_BY_TOPIC[targetTopic] ?? QUESTIONS_BY_TOPIC.factorization;
    const next = candidates[(session.step + 1) % candidates.length];
    session.step += 1;
    session.question_id = next.id;
    return { correct, done: false, next_question: { ...next, options: [...next.options] } };
  }
  sessions.delete(request.session_id);
  return {
    correct, done: true,
    summary: { gaps: copyStates(session.student_id).filter((item) => item.status === 'gap').map((item) => ({ topic_id: item.topic_id, gap_type: item.gap_type ?? 'prerequisite' })) },
  };
}
export async function mockGetLesson(studentId: string, topicId: string, lang: Lang): Promise<Lesson> {
  void studentId;
  return getLesson(topicId, lang);
}
export async function mockTeachBack(request: TeachBackRequest): Promise<TeachBackResponse> {
  const transcript = request.transcript.trim();
  if (!transcript) throw new Error('Write or record a short explanation before submitting.');
  const includesMathCue = /factor|root|zero|square|equation|multiply|product|गुणन|समीकरण|factorization|quadratic/i.test(transcript);
  const score = Math.min(0.88, Math.max(0.35, (transcript.split(/\s+/).length / 35) + (includesMathCue ? 0.24 : 0.12)));
  const covered = includesMathCue ? ['Uses a relevant maths term', 'Attempts to explain the idea in their own words'] : ['Attempts an explanation in their own words'];
  const missing = includesMathCue ? ['Add a worked example to show the rule'] : ['Name the key rule or term', 'Add a short worked example'];
  const now = new Date().toISOString();
  const result = {
    topic_id: request.topic_id, score, covered, missing, errors: [],
    feedback: 'Demo feedback: you have started explaining the idea. Strengthen it by naming the rule and showing one small example. This is a deterministic demonstration, not an AI assessment.',
  };
  const flashcards: Flashcard[] = missing.slice(0, 2).map((point, index) => ({
    id: `teachback-${request.topic_id}-${Date.now()}-${index}`, topic_id: request.topic_id,
    front: `What should you remember about ${TOPIC_BY_ID[request.topic_id]?.name ?? 'this topic'}?`,
    back: point, source: 'teachback',
  }));
  const note: Note = { id: `note-${Date.now()}`, topic_id: request.topic_id, author: 'ai', body: `Demo reflection: ${missing.join('; ')}.`, created_at: now };
  const ownNotes = noteOverrides.get(request.student_id) ?? [];
  ownNotes.push(note);
  noteOverrides.set(request.student_id, ownNotes);
  generatedCards.set(request.student_id, [...(generatedCards.get(request.student_id) ?? []), ...flashcards]);
  const old = copyStates(request.student_id).find((item) => item.topic_id === request.topic_id);
  const mastery = 0.6 * (old?.mastery ?? 0) + 0.4 * score;
  const nextState: TopicState = {
    topic_id: request.topic_id, mastery, confidence: score, gap_type: missing.length ? 'conceptual' : null,
    interval_days: 1, ease: 2.5, next_review: currentDate(), status: mastery < 0.4 ? 'gap' : mastery > 0.8 ? 'mastered' : 'learning',
  };
  updateState(request.student_id, request.topic_id, nextState);
  return { result, flashcards, note, state: nextState };
}
export async function mockGetDueCards(studentId: string): Promise<FlashcardsResponse> {
  return { cards: cardsFor(studentId) };
}
export async function mockReviewCard(request: FlashcardReviewRequest): Promise<FlashcardReviewResponse> {
  reviewedCards.add(`${request.student_id}:${request.card_id}`);
  const card = [...SEED_FLASHCARDS, ...(generatedCards.get(request.student_id) ?? [])].find((item) => item.id === request.card_id);
  const topicId = card?.topic_id ?? 'factorization';
  const state = copyStates(request.student_id).find((item) => item.topic_id === topicId) ?? copyStates(request.student_id)[0];
  const interval = request.quality < 3 ? 1 : state.interval_days <= 0 ? 1 : state.interval_days === 1 ? 6 : Math.max(1, Math.round(state.interval_days * state.ease));
  const ease = Math.max(1.3, state.ease + 0.1 - (5 - request.quality) * (0.08 + (5 - request.quality) * 0.02));
  const nextState = { ...state, interval_days: interval, ease, next_review: currentDate(interval), status: state.status === 'unseen' ? 'learning' : state.status };
  updateState(request.student_id, topicId, nextState);
  return { state: nextState };
}
export async function mockGetNotes(studentId: string, topicId: string): Promise<NotesResponse> {
  hydrateCustomProfile(studentId);
  const seedNotes = isNewLearner(studentId) ? [] : SEED_NOTES;
  const notes = [...seedNotes, ...(noteOverrides.get(studentId) ?? [])].filter((note) => note.topic_id === topicId).sort((a, b) => b.created_at.localeCompare(a.created_at));
  return { notes: notes.map((note) => ({ ...note })) };
}
export async function mockCreateNote(request: NoteCreateRequest): Promise<Note> {
  if (!request.body.trim()) throw new Error('A note cannot be empty.');
  const note: Note = { id: `note-student-${Date.now()}`, topic_id: request.topic_id, author: 'student', body: request.body.trim(), created_at: new Date().toISOString() };
  const ownNotes = noteOverrides.get(request.student_id) ?? [];
  ownNotes.push(note);
  noteOverrides.set(request.student_id, ownNotes);
  return { ...note };
}
export async function mockGetDashboard(studentId: string): Promise<DashboardResponse> {
  const states = copyStates(studentId);
  const total = states.length || 1;
  const weakest = [...states].filter((item) => item.status !== 'unseen').sort((a, b) => a.mastery - b.mastery).slice(0, 3).map((item) => ({ topic_id: item.topic_id, mastery: item.mastery }));
  return {
    overall_mastery: states.reduce((sum, item) => sum + item.mastery, 0) / total,
    topics_mastered: states.filter((item) => item.status === 'mastered').length,
    topics_total: TOPICS.length,
    due_today: cardsFor(studentId).length,
    streak_days: isNewLearner(studentId) ? 0 : 4,
    weakest,
  };
}
export async function mockAdvanceDays(request: AdvanceDaysRequest): Promise<AdvanceDaysResponse> {
  const days = Math.max(0, Math.min(30, Math.floor(request.days)));
  dayOffset += days;
  for (const studentStates of stateOverrides.values()) for (const item of studentStates) {
    if (item.next_review) { const date = new Date(`${item.next_review}T12:00:00Z`); date.setUTCDate(date.getUTCDate() + days); item.next_review = date.toISOString().slice(0, 10); }
  }
  return { new_date: currentDate() };
}

export function getDemoStudentName(studentId: string): string {
  return profileName(studentId);
}
