import type { Question } from '../api/types';

const q = (id: string, topic_id: string, stem: string, options: [string, string, string, string], correct_index: number, difficulty: number, misconception_tags: string[]): Question => ({ id, topic_id, stem, options, correct_index, difficulty, misconception_tags });

/** Small deterministic seed bank for all canonical topics (three questions per topic). */
export const QUESTIONS: Question[] = [
  q('INT-01','integers','What is −7 + 12?',['−19','−5','5','19'],2,1,['signs_added_as_absolute_values']),
  q('INT-02','integers','Which value is smallest?',['−2','0','−9','4'],2,2,['negative_order_reversed']),
  q('INT-03','integers','Evaluate (−3) × (−4).',['−12','−7','7','12'],3,3,['same_sign_product_negative']),
  q('FRA-01','fractions','Which fraction is equivalent to 2/3?',['4/9','6/9','3/6','2/6'],1,1,['numerator_only_scaled']),
  q('FRA-02','fractions','What is 1/4 + 1/2?',['2/6','1/6','3/4','2/4'],2,2,['denominators_added']),
  q('FRA-03','fractions','Simplify 12/18.',['2/3','3/2','6/8','4/9'],0,3,['not_reduced_fully']),
  q('ALG-01','algebraic_expressions','Simplify 3x + 2x.',['5','5x','6x','x'],1,1,['unlike_variable_terms']),
  q('ALG-02','algebraic_expressions','If x = 4, what is 2x + 3?',['11','14','8','7'],0,2,['constant_not_added']),
  q('ALG-03','algebraic_expressions','Expand 2(a + 3).',['2a + 3','a + 6','2a + 6','5a'],2,3,['distribution_incomplete']),
  q('LIN-01','linear_equations','Solve x + 5 = 12.',['17','7','−7','2.4'],1,1,['operation_not_reversed']),
  q('LIN-02','linear_equations','Solve 3x = 21.',['18','7','24','63'],1,2,['division_confused_with_subtraction']),
  q('LIN-03','linear_equations','Solve 2x − 4 = 10.',['3','7','12','−7'],1,3,['constant_moved_wrongly']),
  q('EXP-01','exponents','What is 2³?',['5','6','8','9'],2,1,['exponent_treated_as_multiplication']),
  q('EXP-02','exponents','Simplify x² × x³.',['x⁶','x⁵','x⁵⁄⁶','2x⁵'],1,2,['powers_multiplied_instead_of_added']),
  q('EXP-03','exponents','What is 10⁰?',['0','10','1','100'],2,3,['zero_exponent_as_zero']),
  q('POL-01','polynomials','What is the degree of 4x² + 2x − 1?',['1','2','3','4'],1,1,['coefficient_mistaken_for_degree']),
  q('POL-02','polynomials','Which is a polynomial?',['1/x + 2','√x + 1','3x² − x + 4','x⁻² + 2'],2,2,['negative_or_fractional_exponents_allowed']),
  q('POL-03','polynomials','How many terms are in 2x² + 3x − 5?',['1','2','3','5'],2,3,['terms_counted_by_symbols']),
  q('FAC-01','factorization','Factorize x² + 5x + 6.',['(x + 1)(x + 6)','(x + 2)(x + 3)','(x − 2)(x − 3)','(x + 5)(x + 1)'],1,1,['factors_do_not_sum_to_middle_coefficient']),
  q('FAC-02','factorization','Which expression is equal to 3x + 12?',['3(x + 12)','3(x + 4)','x(3 + 12)','12(3x + 1)'],1,2,['common_factor_not_extracted']),
  q('FAC-03','factorization','Factorize x² − 9.',['(x − 9)(x + 1)','(x − 3)²','(x − 3)(x + 3)','(x − 9)(x + 9)'],2,3,['difference_of_squares_misapplied']),
  q('IDN-01','identities','Which identity is correct?',['(a + b)² = a² + b²','(a + b)² = a² + 2ab + b²','(a − b)² = a² − b²','(a + b)² = 2a + 2b'],1,1,['middle_term_omitted']),
  q('IDN-02','identities','Expand (x − 3)².',['x² − 9','x² − 6x + 9','x² + 6x + 9','x² − 3x + 9'],1,2,['cross_term_sign_wrong']),
  q('IDN-03','identities','Evaluate (p + q)(p − q).',['p² + q²','p² − 2pq + q²','p² − q²','p² + 2pq + q²'],2,3,['difference_of_squares_confused']),
  q('SQR-01','square_roots','What is √49?',['−7','7','24','14'],1,1,['root_confused_with_half']),
  q('SQR-02','square_roots','Simplify √36 + √9.',['√45','9','15','6'],1,2,['radicands_added_first']),
  q('SQR-03','square_roots','Which is equal to √(25 × 4)?',['10','20','29','5'],0,3,['square_root_product_misread']),
  q('QUA-01','quadratic_equations','Which is a quadratic equation in standard form?',['2x + 3 = 0','x² − 5x + 6 = 0','x³ + x = 0','5 = 0'],1,1,['degree_not_two']),
  q('QUA-02','quadratic_equations','In 2x² + 3x − 7 = 0, what is a?',['3','−7','2','0'],2,2,['coefficients_misidentified']),
  q('QUA-03','quadratic_equations','For x² − 4 = 0, which are the roots?',['4 and 0','2 and −2','2 and 2','−4 and 1'],1,3,['constant_treated_as_root']),
  q('SBF-01','solve_by_factorization','Solve x² − 5x + 6 = 0.',['x = 1, 6','x = −2, −3','x = 2, 3','x = −2, 3'],2,2,['factor_pair_sum_wrong']),
  q('SBF-02','solve_by_factorization','If (x − 4)(x + 1) = 0, what can x equal?',['4 or −1','−4 or 1','4 only','−1 only'],0,1,['zero_product_rule_misapplied']),
  q('SBF-03','solve_by_factorization','Which factorization matches x² + x − 12?',['(x + 6)(x − 2)','(x + 4)(x − 3)','(x − 4)(x + 3)','(x + 12)(x − 1)'],1,3,['factors_sum_not_middle_coefficient']),
  q('QF-01','quadratic_formula','For ax² + bx + c = 0, the quadratic formula uses which denominator?',['a','2a','−2a','b'],1,1,['denominator_coefficient_confused']),
  q('QF-02','quadratic_formula','For x² − 3x + 2 = 0, what is the discriminant?',['1','−1','17','0'],0,2,['discriminant_sign_error']),
  q('QF-03','quadratic_formula','In the formula, what appears under the square root?',['b² + 4ac','b − 4ac','b² − 4ac','4ac − b'],2,3,['discriminant_formula_misremembered']),
  q('DIS-01','discriminant','If b² − 4ac is positive, a quadratic has…',['no real roots','one repeated real root','two distinct real roots','always complex coefficients'],2,1,['positive_discriminant_misread']),
  q('DIS-02','discriminant','What is the discriminant of x² + 4x + 4 = 0?',['16','8','0','−4'],2,2,['discriminant_not_substituted_correctly']),
  q('DIS-03','discriminant','If the discriminant equals zero, the roots are…',['two distinct real roots','one repeated real root','no real roots','always integers'],1,3,['zero_discriminant_as_no_roots']),
];

export const QUESTIONS_BY_ID = Object.fromEntries(QUESTIONS.map((question) => [question.id, question])) as Record<string, Question>;
export const QUESTIONS_BY_TOPIC = QUESTIONS.reduce<Record<string, Question[]>>((acc, question) => {
  (acc[question.topic_id] ??= []).push(question);
  return acc;
}, {});
