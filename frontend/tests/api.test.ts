import { beforeEach, describe, expect, it } from 'vitest';
import { api, MOCK_MODE } from '../src/api/client';

describe('API adapter in mock mode', () => {
  beforeEach(() => { localStorage.clear(); });
  it('uses the mock adapter when configured for a standalone demo', async () => {
    expect(MOCK_MODE).toBe(true);
    const graph = await api.getGraph('demo-aarav');
    expect(graph.topics).toHaveLength(13);
    expect(graph.states.some((state) => state.topic_id === 'factorization' && state.status === 'gap')).toBe(true);
  });
  it('runs the deterministic backtrace demo after a wrong answer', async () => {
    const started = await api.startDiagnostic({ student_id: 'demo-aarav', topic_id: 'solve_by_factorization' });
    const result = await api.answerDiagnostic({ session_id: started.session_id, question_id: started.question.id, chosen_index: (started.question.correct_index + 1) % 4, time_ms: 1000 });
    expect(result.correct).toBe(false);
    expect(result.backtrace?.from_topic_id).toBe('solve_by_factorization');
    expect(result.backtrace?.to_topic_id).toBe('factorization');
    expect(result.next_question?.topic_id).toBe('factorization');
  });
  it('returns lesson content with contract-shaped exercise questions', async () => {
    const lesson = await api.getLesson('demo-aarav', 'factorization', 'en');
    expect(lesson.topic_id).toBe('factorization');
    expect(lesson.exercises.length).toBeGreaterThan(0);
    expect(lesson.exercises[0].options).toHaveLength(4);
  });
});
