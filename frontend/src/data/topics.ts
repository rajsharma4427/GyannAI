import type { Topic } from '../api/types';

/** Canonical IDs and prerequisites from the shared contract — do not rename these IDs. */
export const TOPICS: Topic[] = [
  { id: 'integers', name: 'Integers and sign rules', prereq_ids: [], description: 'Work confidently with positive and negative numbers.' },
  { id: 'fractions', name: 'Fractions and ratios', prereq_ids: [], description: 'Compare, simplify, and operate on fractions and ratios.' },
  { id: 'algebraic_expressions', name: 'Algebraic expressions', prereq_ids: ['integers'], description: 'Read, simplify, and combine expressions with variables.' },
  { id: 'linear_equations', name: 'Linear equations in one variable', prereq_ids: ['algebraic_expressions', 'fractions'], description: 'Keep an equation balanced while isolating the variable.' },
  { id: 'exponents', name: 'Exponents and squares', prereq_ids: ['integers'], description: 'Use powers, square numbers, and exponent rules.' },
  { id: 'polynomials', name: 'Polynomials and degree', prereq_ids: ['algebraic_expressions', 'exponents'], description: 'Recognise terms, coefficients, and polynomial degree.' },
  { id: 'factorization', name: 'Factorization', prereq_ids: ['polynomials'], description: 'Rewrite expressions as products of simpler factors.' },
  { id: 'identities', name: 'Algebraic identities', prereq_ids: ['polynomials', 'exponents'], description: 'Use identities to expand and simplify expressions efficiently.' },
  { id: 'square_roots', name: 'Square roots', prereq_ids: ['exponents'], description: 'Understand square roots and simplify perfect squares.' },
  { id: 'quadratic_equations', name: 'Quadratic equations (standard form)', prereq_ids: ['polynomials', 'linear_equations'], description: 'Recognise ax² + bx + c = 0 and what makes it quadratic.' },
  { id: 'solve_by_factorization', name: 'Solving by factorization', prereq_ids: ['quadratic_equations', 'factorization'], description: 'Find roots by writing a quadratic as two factors.' },
  { id: 'quadratic_formula', name: 'Solving by the quadratic formula', prereq_ids: ['quadratic_equations', 'square_roots'], description: 'Apply the quadratic formula when factoring is not convenient.' },
  { id: 'discriminant', name: 'Discriminant and nature of roots', prereq_ids: ['quadratic_formula'], description: 'Use b² − 4ac to predict the roots of a quadratic.' },
];

export const TOPIC_BY_ID = Object.fromEntries(TOPICS.map((topic) => [topic.id, topic])) as Record<string, Topic>;

export const TOPIC_GROUPS = [
  { label: 'Foundations', ids: ['integers', 'fractions', 'algebraic_expressions', 'linear_equations', 'exponents'] },
  { label: 'Build fluency', ids: ['polynomials', 'factorization', 'identities', 'square_roots'] },
  { label: 'Quadratics', ids: ['quadratic_equations', 'solve_by_factorization', 'quadratic_formula', 'discriminant'] },
] as const;
