import { describe, expect, it } from 'vitest';
import { TOPICS } from '../src/data/topics';
import { QUESTIONS } from '../src/data/questions';

function hasCycle() {
  const byId = new Map(TOPICS.map((topic) => [topic.id, topic]));
  const visiting = new Set<string>();
  const visited = new Set<string>();
  const visit = (id: string): boolean => {
    if (visiting.has(id)) return true;
    if (visited.has(id)) return false;
    visiting.add(id);
    for (const prereq of byId.get(id)?.prereq_ids ?? []) if (visit(prereq)) return true;
    visiting.delete(id); visited.add(id); return false;
  };
  return TOPICS.some((topic) => visit(topic.id));
}

describe('canonical topic data', () => {
  it('contains exactly the 13 shared canonical topic IDs', () => {
    expect(TOPICS.map((topic) => topic.id)).toEqual([
      'integers', 'fractions', 'algebraic_expressions', 'linear_equations', 'exponents', 'polynomials',
      'factorization', 'identities', 'square_roots', 'quadratic_equations', 'solve_by_factorization',
      'quadratic_formula', 'discriminant',
    ]);
  });
  it('uses only valid prerequisite IDs and has no cycles', () => {
    const ids = new Set(TOPICS.map((topic) => topic.id));
    expect(TOPICS.every((topic) => topic.prereq_ids.every((id) => ids.has(id)))).toBe(true);
    expect(hasCycle()).toBe(false);
  });
  it('has three seeded, four-option questions per canonical topic', () => {
    for (const topic of TOPICS) {
      const questions = QUESTIONS.filter((question) => question.topic_id === topic.id);
      expect(questions).toHaveLength(3);
      for (const question of questions) {
        expect(question.options).toHaveLength(4);
        expect(question.correct_index).toBeGreaterThanOrEqual(0);
        expect(question.correct_index).toBeLessThan(4);
      }
    }
  });
});
