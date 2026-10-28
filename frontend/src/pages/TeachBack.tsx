import { useEffect, useState, type FormEvent } from 'react';
import { ArrowRight, CheckCircle2, Mic, MicOff, RotateCcw, Send, Sparkles, Volume2 } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { api, MOCK_MODE } from '../api/client';
import type { TeachBackResponse } from '../api/types';
import { TOPIC_BY_ID } from '../data/topics';
import { useAppStore } from '../store/useApp';
import { useSpeechRecognition, useSpeechSynthesis } from '../hooks/speech';
import { addActivity } from '../utils/activity';
import { PageHeader } from '../components/PageHeader';

const SAMPLE_EXPLANATIONS: Record<string, string> = {
  factorization: 'Factorization means breaking down an expression into smaller factors that multiply together to make the original expression. For x squared plus 5x plus 6, we find two numbers that multiply to 6 and add to 5, which are 2 and 3, giving the factors x plus 2 times x plus 3.',
  linear_equations: 'A linear equation represents a balanced weighing scale with an equals sign. To keep the equation balanced and solve for x, whatever operation you perform on one side, you must perform on the other side too.',
  quadratic_equations: 'A quadratic equation is a polynomial of degree two in the standard form ax squared plus bx plus c equals 0, where the coefficient a is not zero. We can solve it by factoring, by completing the square, or with the quadratic formula.',
  solve_by_factorization: 'To solve a quadratic equation by factoring, we rewrite it as two factors equal to zero: x plus 2 times x plus 3 equals 0. By the zero product rule, at least one factor must be zero, so x plus 2 is zero giving x equals minus 2, or x plus 3 is zero giving x equals minus 3.',
  quadratic_formula: 'The quadratic formula is x equals minus b plus or minus square root of b squared minus 4ac, all divided by 2a. The expression under the square root is the discriminant which tells us whether the roots are real or repeated.',
  discriminant: 'The discriminant is D equals b squared minus 4ac. When D is greater than zero there are two distinct real roots. When D equals zero there is one repeated real root. When D is negative there are no real roots.',
  integers: 'Integers are positive and negative whole numbers including zero. The most important rule when adding and subtracting integers is to carefully track whether signs are positive or negative.',
  fractions: 'A fraction represents part of a whole with a numerator over a denominator. When adding or subtracting fractions, we must first convert them to a common denominator.',
  algebraic_expressions: 'An algebraic expression combines variables, numbers, and operational symbols without an equals sign. We simplify it by grouping and combining like terms.',
  exponents: 'An exponent tells us how many times a base number is multiplied by itself. The product law says that when multiplying powers with the same base, we add their exponents.',
  polynomials: 'A polynomial is an expression with one or more algebraic terms where variable powers are non-negative integers.',
  identities: 'An algebraic identity is an equation that is true for all possible values of its variables, like a plus b whole squared equals a squared plus 2ab plus b squared.',
  square_roots: 'The square root of a number is a value that gives the original number when multiplied by itself. Every positive number has both a positive and negative root.',
};

export function TeachBackPage() {
  const { topicId = 'quadratic_equations' } = useParams();
  const { studentId, lang } = useAppStore();
  const [text, setText] = useState('');
  const [result, setResult] = useState<TeachBackResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const topic = TOPIC_BY_ID[topicId] ?? TOPIC_BY_ID.quadratic_equations;
  const speech = useSpeechRecognition(lang);
  const synthesis = useSpeechSynthesis(lang);

  // Sync recognized or simulated speech transcript into text area
  useEffect(() => {
    if (speech.transcript) {
      setText(speech.transcript);
    }
  }, [speech.transcript]);

  useEffect(() => () => {
    speech.stop();
    synthesis.cancel();
  }, [speech, synthesis]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!text.trim()) {
      setError('Add a few words about the concept before submitting.');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const response = await api.submitTeachBack({
        student_id: studentId,
        topic_id: topic.id,
        transcript: text.trim(),
      });
      setResult(response);
      addActivity('Completed teach-back', topic.name);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Your explanation could not be checked.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSimulateSample = () => {
    const sample = SAMPLE_EXPLANATIONS[topic.id] ?? SAMPLE_EXPLANATIONS.quadratic_equations;
    setError('');
    speech.simulate(sample);
  };

  if (result) {
    return (
      <div className="page-stack">
        <PageHeader
          eyebrow="TEACH-BACK · FEEDBACK"
          title="You made the idea your own."
          description="Use this reflection to decide what to practise next. A score is only one small signal."
          action={
            <button
              className="button button-secondary button-small"
              onClick={() => {
                setResult(null);
                setText('');
                speech.reset();
              }}
            >
              <RotateCcw size={15} /> Try again
            </button>
          }
        />
        <section className="teachback-result-panel panel">
          <div className="result-score">
            <span className="score-ring">
              <strong>{Math.round(result.result.score * 100)}<small>%</small></strong>
            </span>
            <div>
              <span className="eyebrow">{MOCK_MODE ? 'DEMO FEEDBACK' : 'YOUR REFLECTION'}</span>
              <h2>Here’s what to build on</h2>
              <p>{result.result.feedback}</p>
              {MOCK_MODE && <span className="demo-disclaimer">This is deterministic demo feedback, not an AI assessment.</span>}
            </div>
          </div>
          <div className="feedback-columns">
            <section className="feedback-list feedback-list-positive">
              <h3><CheckCircle2 size={17} /> You touched on</h3>
              {result.result.covered.length ? (
                result.result.covered.map((item) => (
                  <p key={item}><CheckCircle2 size={15} />{item}</p>
                ))
              ) : (
                <p>No concepts were marked as covered yet.</p>
              )}
            </section>
            <section className="feedback-list feedback-list-improve">
              <h3><Sparkles size={17} /> Try adding</h3>
              {result.result.missing.length ? (
                result.result.missing.map((item) => (
                  <p key={item}><span className="feedback-bullet" />{item}</p>
                ))
              ) : (
                <p>Nothing specific was flagged.</p>
              )}
            </section>
          </div>
          <div className="submitted-words">
            <span className="eyebrow">YOUR EXPLANATION</span>
            <p>{text}</p>
          </div>
          {result.flashcards.length > 0 && (
            <div className="generated-cards">
              <span className="eyebrow">ADDED TO REVISION</span>
              <div>
                {result.flashcards.map((card) => (
                  <article key={card.id}>
                    <strong>{card.front}</strong>
                    <p>{card.back}</p>
                  </article>
                ))}
              </div>
            </div>
          )}
          <div className="result-actions">
            <Link className="button button-primary" to="/review">
              Review flashcards <ArrowRight size={16} />
            </Link>
            <Link className="button button-secondary" to={`/lesson/${topic.id}`}>
              Revisit lesson
            </Link>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="TEACH IT BACK"
        title="Explain it in your own words."
        description={`Tell us how you understand ${topic.name.toLowerCase()}. It doesn't need to sound like a textbook.`}
        action={
          <Link className="button button-secondary button-small" to={`/lesson/${topic.id}`}>
            <ArrowRight size={15} /> Revisit lesson
          </Link>
        }
      />
      <div className="teachback-layout">
        <section className="teachback-main panel">
          <div className="teachback-prompt">
            <span className="teachback-prompt-icon"><Sparkles size={20} /></span>
            <div>
              <span className="eyebrow">A GENTLE PROMPT</span>
              <h2>How would you explain this to a friend?</h2>
              <p>What is the main idea? Which steps matter? Can you add a small example?</p>
            </div>
          </div>

          <div className="voice-recorder">
            <div className={`mic-visual ${speech.listening ? 'mic-listening' : ''}`}>
              <span className="mic-ripple" />
              <span className="mic-core"><Mic size={25} /></span>
            </div>
            <div className="voice-recorder-copy">
              <strong>
                {speech.listening
                  ? 'Listening to your explanation…'
                  : speech.supported
                    ? 'Speak your explanation'
                    : 'Voice input ready'}
              </strong>
              <p>
                {speech.listening
                  ? 'Speak naturally into your microphone. Stop when you have finished.'
                  : speech.supported
                    ? 'Click "Start speaking" to record, or "Sample voice" to simulate.'
                    : 'Use "Sample voice explanation" below or type directly.'}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
              {speech.listening ? (
                <button type="button" className="button button-danger" onClick={() => speech.stop()}>
                  <MicOff size={16} /> Stop recording
                </button>
              ) : (
                <button
                  type="button"
                  className="button button-primary"
                  onClick={() => {
                    speech.reset();
                    setText('');
                    setError('');
                    speech.start();
                  }}
                  disabled={!speech.supported}
                  title={speech.supported ? 'Record using microphone' : 'Microphone input not available in this browser'}
                >
                  <Mic size={16} /> Start speaking
                </button>
              )}
              <button
                type="button"
                className="button button-secondary"
                onClick={handleSimulateSample}
                title="Simulate speaking this topic's explanation aloud"
              >
                <Sparkles size={16} /> Sample voice
              </button>
            </div>
          </div>

          {speech.error && (
            <p className="inline-error" style={{ margin: '8px 0 12px' }} role="alert">
              {speech.error}
            </p>
          )}

          <div className="transcript-status" role="status">
            <span className={`recording-indicator ${speech.listening ? 'recording-indicator-on' : ''}`} />
            {speech.listening
              ? 'Microphone active · streaming your words below'
              : speech.supported
                ? 'Microphone ready'
                : 'Text & voice sample mode ready'}
            {speech.interim && <em> “{speech.interim}”</em>}
          </div>

          <form onSubmit={submit} className="teachback-form">
            <label htmlFor="teachback-text">Your explanation</label>
            <textarea
              id="teachback-text"
              value={text}
              onChange={(event) => setText(event.target.value)}
              rows={7}
              placeholder={`For example: ${SAMPLE_EXPLANATIONS[topic.id] ?? 'Explain the rule in your own words, and show one worked example…'}`}
            />
            <div className="form-footer">
              <span className="muted tiny">
                {text.trim() ? text.trim().split(/\s+/).length : 0} words · Edit the transcript before submitting
              </span>
              <button className="button button-primary" type="submit" disabled={submitting || !text.trim()}>
                {submitting ? 'Reflecting…' : 'Submit explanation'} <Send size={16} />
              </button>
            </div>
            {error && <p className="inline-error" role="alert">{error}</p>}
          </form>

          <div className="privacy-note">
            <CheckCircle2 size={15} />
            <span>Your words are used for this learning activity. In mock mode, feedback is evaluated with deterministic semantic criteria.</span>
          </div>
        </section>

        <aside className="teachback-aside">
          <div className="aside-tip-card">
            <span className="eyebrow">A HELPFUL STRUCTURE</span>
            <h3>Three parts are enough.</h3>
            <div className="tip-step">
              <span>1</span>
              <div>
                <strong>The idea</strong>
                <p>Say what the concept means.</p>
              </div>
            </div>
            <div className="tip-step">
              <span>2</span>
              <div>
                <strong>The process</strong>
                <p>Describe one or two key steps.</p>
              </div>
            </div>
            <div className="tip-step">
              <span>3</span>
              <div>
                <strong>An example</strong>
                <p>Use a small number or expression.</p>
              </div>
            </div>
            <button
              type="button"
              className="button button-secondary button-block"
              onClick={() =>
                synthesis.speak(
                  `The main idea of ${topic.name} is this: ${SAMPLE_EXPLANATIONS[topic.id] ?? topic.description}. Explain the rule in your own words, then show one small example.`
                )
              }
              disabled={!synthesis.supported}
            >
              <Volume2 size={16} /> {synthesis.speaking ? 'Playing prompt…' : 'Hear the prompt'}
            </button>
          </div>
          <div className="aside-tip-small">
            <strong>There’s no perfect wording.</strong>
            <p>The goal is to notice what feels clear and what deserves another look.</p>
          </div>
        </aside>
      </div>
    </div>
  );
}
