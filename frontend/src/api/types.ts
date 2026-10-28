/** Shared REST contract copied from the Gyaan Loop build plan (Section 3). */
export type Lang = 'en' | 'hi' | 'hinglish';
export type GapType = 'conceptual' | 'procedural' | 'careless' | 'prerequisite';
export type TopicStatus = 'unseen' | 'gap' | 'learning' | 'mastered';
export type NoteAuthor = 'ai' | 'student';
export type FlashcardSource = 'gap' | 'teachback';

export interface Topic {
  id: string;
  name: string;
  parent_id?: string | null;
  prereq_ids: string[];
  description: string;
}

export interface Question {
  id: string;
  topic_id: string;
  stem: string;
  options: [string, string, string, string] | string[];
  correct_index: number;
  difficulty: number;
  misconception_tags: string[];
}

export interface MistakeAnalysis {
  gap_type: GapType;
  suspected_prereq_id?: string | null;
  reason: string;
}

export interface Lesson {
  topic_id: string;
  story: string;
  explanation: string;
  key_terms: string[];
  exercises: Question[];
}

export interface TeachBackResult {
  topic_id: string;
  score: number;
  covered: string[];
  missing: string[];
  errors: string[];
  feedback: string;
}

export interface Flashcard {
  id: string;
  topic_id: string;
  front: string;
  back: string;
  source: FlashcardSource;
}

export interface Note {
  id: string;
  topic_id: string;
  author: NoteAuthor;
  body: string;
  created_at: string;
}

export interface TopicState {
  topic_id: string;
  mastery: number;
  confidence: number;
  gap_type?: GapType | null;
  interval_days: number;
  ease: number;
  next_review?: string | null;
  status: TopicStatus;
}

export interface StudentCreateRequest {
  name: string;
  lang: Lang;
}
export interface StudentCreateResponse { student_id: string; }
export interface SyllabusRequest {
  student_id: string;
  text?: string;
  goal?: string;
}
export interface SyllabusResponse { topics: Topic[]; }
export interface GraphResponse { topics: Topic[]; states: TopicState[]; }
export interface DiagnosticStartRequest { student_id: string; topic_id: string; }
export interface DiagnosticStartResponse { session_id: string; question: Question; }
export interface Backtrace {
  from_topic_id: string;
  to_topic_id: string;
  reason: string;
}
export interface DiagnosticAnswerRequest {
  session_id: string;
  question_id: string;
  chosen_index: number;
  time_ms: number;
}
export interface DiagnosticAnswerResponse {
  correct: boolean;
  done: boolean;
  next_question?: Question | null;
  backtrace?: Backtrace | null;
  summary?: { gaps: Array<{ topic_id: string; gap_type: GapType }> } | null;
}
export interface TeachBackRequest { student_id: string; topic_id: string; transcript: string; }
export interface TeachBackResponse {
  result: TeachBackResult;
  flashcards: Flashcard[];
  note: Note;
  state: TopicState;
}
export interface FlashcardsResponse { cards: Flashcard[]; }
export interface FlashcardReviewRequest { student_id: string; card_id: string; quality: number; }
export interface FlashcardReviewResponse { state: TopicState; }
export interface NotesResponse { notes: Note[]; }
export interface NoteCreateRequest { student_id: string; topic_id: string; body: string; }
export interface DashboardResponse {
  overall_mastery: number;
  topics_mastered: number;
  topics_total: number;
  due_today: number;
  streak_days: number;
  weakest: Array<{ topic_id: string; mastery: number }>;
}
export interface AdvanceDaysRequest { student_id: string; days: number; }
export interface AdvanceDaysResponse { new_date: string; }
export interface ApiErrorBody { error: string; code: string; }

/** UI-only demo profile metadata; this is not part of the backend contract. */
export interface DemoProfile {
  student_id: string;
  name: string;
  description: string;
  kind: 'returning' | 'new';
}
