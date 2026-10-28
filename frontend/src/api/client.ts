import type {
  AdvanceDaysRequest, AdvanceDaysResponse, DashboardResponse, DiagnosticAnswerRequest,
  DiagnosticAnswerResponse, DiagnosticStartRequest, DiagnosticStartResponse, FlashcardReviewRequest,
  FlashcardReviewResponse, FlashcardsResponse, GraphResponse, Lang, Lesson, Note,
  NoteCreateRequest, NotesResponse, StudentCreateRequest, StudentCreateResponse, SyllabusRequest,
  SyllabusResponse, TeachBackRequest, TeachBackResponse,
} from './types';
import * as mock from './mock';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
export const MOCK_MODE = ['true', '1'].includes((import.meta.env.VITE_MOCK ?? 'true').toLowerCase());

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { ...(init.body ? { 'Content-Type': 'application/json' } : {}), ...init.headers },
    });
  } catch {
    throw new Error(`Could not reach the Gyaan Loop backend at ${API_BASE_URL}. Check that Person 2's server is running, or enable mock mode.`);
  }
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      const body = await response.json() as { error?: string; code?: string };
      if (body.error) message = body.error;
    } catch { /* response was not a JSON error */ }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}
const post = <T>(path: string, body: unknown) => request<T>(path, { method: 'POST', body: JSON.stringify(body) });

/** The only frontend module allowed to call the backend. Endpoint paths follow Section 3 exactly. */
export const api = {
  createStudent: (body: StudentCreateRequest): Promise<StudentCreateResponse> => MOCK_MODE ? mock.mockCreateStudent(body) : post<StudentCreateResponse>('/api/students', body),
  createSyllabus: (body: SyllabusRequest): Promise<SyllabusResponse> => MOCK_MODE ? mock.mockCreateSyllabus(body) : post<SyllabusResponse>('/api/syllabus', body),
  getGraph: (studentId: string): Promise<GraphResponse> => MOCK_MODE ? mock.mockGetGraph(studentId) : request<GraphResponse>(`/api/graph/${encodeURIComponent(studentId)}`),
  startDiagnostic: (body: DiagnosticStartRequest): Promise<DiagnosticStartResponse> => MOCK_MODE ? mock.mockStartDiagnostic(body) : post<DiagnosticStartResponse>('/api/diagnostic/start', body),
  answerDiagnostic: (body: DiagnosticAnswerRequest): Promise<DiagnosticAnswerResponse> => MOCK_MODE ? mock.mockAnswerDiagnostic(body) : post<DiagnosticAnswerResponse>('/api/diagnostic/answer', body),
  getLesson: (studentId: string, topicId: string, lang: Lang): Promise<Lesson> => MOCK_MODE ? mock.mockGetLesson(studentId, topicId, lang) : request<Lesson>(`/api/lesson/${encodeURIComponent(studentId)}/${encodeURIComponent(topicId)}?lang=${lang}`),
  submitTeachBack: (body: TeachBackRequest): Promise<TeachBackResponse> => MOCK_MODE ? mock.mockTeachBack(body) : post<TeachBackResponse>('/api/teachback', body),
  getDueCards: (studentId: string): Promise<FlashcardsResponse> => MOCK_MODE ? mock.mockGetDueCards(studentId) : request<FlashcardsResponse>(`/api/flashcards/due/${encodeURIComponent(studentId)}`),
  reviewCard: (body: FlashcardReviewRequest): Promise<FlashcardReviewResponse> => MOCK_MODE ? mock.mockReviewCard(body) : post<FlashcardReviewResponse>('/api/flashcards/review', body),
  getNotes: (studentId: string, topicId: string): Promise<NotesResponse> => MOCK_MODE ? mock.mockGetNotes(studentId, topicId) : request<NotesResponse>(`/api/notes/${encodeURIComponent(studentId)}/${encodeURIComponent(topicId)}`),
  createNote: (body: NoteCreateRequest): Promise<Note> => MOCK_MODE ? mock.mockCreateNote(body) : post<Note>('/api/notes', body),
  getDashboard: (studentId: string): Promise<DashboardResponse> => MOCK_MODE ? mock.mockGetDashboard(studentId) : request<DashboardResponse>(`/api/dashboard/${encodeURIComponent(studentId)}`),
  advanceDays: (body: AdvanceDaysRequest): Promise<AdvanceDaysResponse> => MOCK_MODE ? mock.mockAdvanceDays(body) : post<AdvanceDaysResponse>('/api/dev/advance-days', body),
};

export function getApiBaseUrl() { return API_BASE_URL; }
