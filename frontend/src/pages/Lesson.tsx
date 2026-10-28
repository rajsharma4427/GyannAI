import { useEffect, useState } from 'react';
import { ArrowLeft, ArrowRight, BookOpen, CheckCircle2, Headphones, Pause, Volume2 } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { api, MOCK_MODE } from '../api/client';
import type { Lesson as LessonType } from '../api/types';
import { TOPIC_BY_ID } from '../data/topics';
import { useAppStore } from '../store/useApp';
import { useSpeechSynthesis } from '../hooks/speech';
import { addActivity } from '../utils/activity';
import { PageHeader } from '../components/PageHeader';
import { ErrorState, LoadingState } from '../components/StateMessage';

const workedExamples: Record<string, { prompt: string; steps: string[]; result: string }> = {
  factorization: { prompt: 'Factorize x² + 5x + 6', steps: ['Find two numbers that multiply to 6.', 'Those numbers must also add to 5.', 'The pair is 2 and 3, so write one factor for each number.'], result: '(x + 2)(x + 3)' },
  linear_equations: { prompt: 'Solve 2x + 4 = 14', steps: ['Subtract 4 from both sides: 2x = 10.', 'Divide both sides by 2.', 'Check by replacing x with 5 in the original equation.'], result: 'x = 5' },
  quadratic_equations: { prompt: 'Write x² − 5x + 6 as a quadratic in standard form', steps: ['Compare the equation with ax² + bx + c = 0.', 'Identify the coefficients: a = 1, b = −5, c = 6.', 'The coefficient a cannot be zero for a quadratic equation.'], result: 'a = 1, b = −5, c = 6' },
  solve_by_factorization: { prompt: 'Solve x² − 5x + 6 = 0', steps: ['Factor the expression: (x − 2)(x − 3) = 0.', 'Set each factor equal to zero.', 'Solve x − 2 = 0 and x − 3 = 0.'], result: 'x = 2 or x = 3' },
  quadratic_formula: { prompt: 'Use the formula for ax² + bx + c = 0', steps: ['Identify a, b and c from the equation.', 'Calculate D = b² − 4ac under the square root.', 'Substitute carefully into x = (−b ± √D) / 2a.'], result: 'x = (−b ± √(b² − 4ac)) / 2a' },
  discriminant: { prompt: 'Find the discriminant for x² + 4x + 4 = 0', steps: ['Identify a = 1, b = 4 and c = 4.', 'Calculate D = b² − 4ac.', 'D = 16 − 16 = 0, so the equation has one repeated real root.'], result: 'D = 0 · one repeated real root' },
};

export function LessonPage() {
  const { topicId = 'quadratic_equations' } = useParams();
  const { studentId, lang, setLang } = useAppStore();
  const [lesson, setLesson] = useState<LessonType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [practiceChoice, setPracticeChoice] = useState<number | null>(null);
  const [practiceSubmitted, setPracticeSubmitted] = useState(false);
  const { supported: speechSupported, speaking, speak, cancel } = useSpeechSynthesis(lang);
  const topic = TOPIC_BY_ID[topicId] ?? TOPIC_BY_ID.quadratic_equations;
  const load = async () => { setLoading(true); setError(''); setPracticeChoice(null); setPracticeSubmitted(false); try { setLesson(await api.getLesson(studentId, topic.id, lang)); } catch (cause) { setError(cause instanceof Error ? cause.message : 'The lesson could not be loaded.'); } finally { setLoading(false); } };
  useEffect(() => { void load(); return () => cancel(); }, [studentId, topic.id, lang]);
  const example = workedExamples[topic.id] ?? { prompt: `Apply the key idea in ${topic.name.toLowerCase()}`, steps: ['Identify what the question gives you.', 'Choose the rule that matches the concept.', 'Check your result against the original question.'], result: 'Explain why the result makes sense.' };
  const translationAvailable = lang === 'en' || ['factorization', 'quadratic_equations'].includes(topic.id);
  const activeQuestion = lesson?.exercises?.[0];

  return <div className="page-stack">
    <PageHeader eyebrow="LEARN THE IDEA" title={topic.name} description={topic.description} action={<Link className="button button-secondary button-small" to="/topics"><ArrowLeft size={15} /> All topics</Link>} />
    {loading ? <LoadingState label="Opening your lesson…" /> : error || !lesson ? <ErrorState message={error || 'No lesson content was returned.'} onRetry={() => void load()} /> : <>
      <div className="lesson-toolbar"><div className="lesson-breadcrumb"><span>Maths track</span><ArrowRight size={13} /><span>{topic.name}</span></div><div className="lesson-tool-actions"><label htmlFor="lesson-language">Lesson language</label><select id="lesson-language" value={lang} onChange={(event) => setLang(event.target.value as 'en' | 'hi' | 'hinglish')}><option value="en">English</option><option value="hi">हिन्दी</option><option value="hinglish">Hinglish</option></select><button className="button button-secondary button-small" onClick={() => speaking ? cancel() : speak(`${lesson.story} ${lesson.explanation}`)} disabled={!speechSupported}>{speaking ? <Pause size={15} /> : <Volume2 size={15} />}{speaking ? 'Stop listening' : 'Listen to lesson'}</button></div></div>
      {!translationAvailable && <div className="translation-note" role="status">This topic’s full lesson is currently available in English only. The language preference is saved, but this content has not been translated yet.</div>}
      <div className="lesson-layout">
        <article className="lesson-main">
          <section className="lesson-story-card"><div className="lesson-story-heading"><span className="story-icon"><Headphones size={17} /></span><span className="eyebrow">THE BIG IDEA</span><span className="story-time">~1 min</span></div><p className="lesson-story-text">{lesson.story}</p><div className="story-footnote"><span className="story-footnote-line" />A simple way to picture the concept</div></section>
          <section className="lesson-section"><div className="lesson-section-heading"><span className="lesson-number">01</span><div><span className="eyebrow">UNDERSTAND</span><h2>What’s happening?</h2></div></div><p className="lesson-explanation">{lesson.explanation}</p><div className="key-term-row"><span>Key terms</span>{lesson.key_terms.map((term) => <span className="key-term" key={term}>{term}</span>)}</div></section>
          <section className="worked-example-card"><div className="worked-example-top"><div><span className="eyebrow">WORKED EXAMPLE</span><h2>{example.prompt}</h2></div><span className="worked-example-mark"><BookOpen size={18} /></span></div><div className="worked-steps">{example.steps.map((step, index) => <div className="worked-step" key={step}><span>{index + 1}</span><p>{step}</p></div>)}</div><div className="worked-result"><span>Result</span><strong>{example.result}</strong></div></section>
          <section className="lesson-practice"><div className="lesson-section-heading"><span className="lesson-number">02</span><div><span className="eyebrow">YOUR TURN</span><h2>Try one yourself</h2></div></div>{activeQuestion ? <><p className="practice-question-stem">{activeQuestion.stem}</p><div className="practice-options">{activeQuestion.options.map((option, index) => <button key={`${activeQuestion.id}-${index}`} className={`practice-option ${practiceChoice === index ? 'practice-option-selected' : ''} ${practiceSubmitted && index === activeQuestion.correct_index ? 'practice-option-correct' : ''} ${practiceSubmitted && practiceChoice === index && index !== activeQuestion.correct_index ? 'practice-option-wrong' : ''}`} onClick={() => !practiceSubmitted && setPracticeChoice(index)} disabled={practiceSubmitted} aria-pressed={practiceChoice === index}><span>{String.fromCharCode(65 + index)}</span>{option}</button>)}</div>{practiceSubmitted && <p className={`practice-result ${practiceChoice === activeQuestion.correct_index ? 'practice-result-good' : ''}`} role="status">{practiceChoice === activeQuestion.correct_index ? 'Correct — you’ve got the key idea.' : `The correct answer is ${activeQuestion.options[activeQuestion.correct_index]}. Revisit the worked example, then give it another try in a diagnostic.`}</p>}<div className="practice-footer">{!practiceSubmitted ? <button className="button button-primary" disabled={practiceChoice === null} onClick={() => { setPracticeSubmitted(true); addActivity('Practised lesson question', topic.name); }}>Check answer <CheckCircle2 size={16} /></button> : <Link className="button button-primary" to={`/diagnostic/${topic.id}`}>Try a diagnostic <ArrowRight size={16} /></Link>}</div></> : <p className="muted">Practice questions are not available in this lesson yet.</p>}</section>
        </article>
        <aside className="lesson-aside"><div className="lesson-aside-card"><span className="aside-card-icon"><CheckCircle2 size={18} /></span><span className="eyebrow">AFTER THIS LESSON</span><h3>Make the idea stick.</h3><p>Explain it in your own words. Teaching back a concept can reveal which part needs another look.</p><Link to={`/teach-back/${topic.id}`} className="button button-primary button-block">Try teach-back <ArrowRight size={15} /></Link></div><div className="lesson-aside-card lesson-related-card"><span className="eyebrow">KEEP EXPLORING</span><h3>Related prerequisites</h3>{topic.prereq_ids.length ? topic.prereq_ids.map((id) => <Link to={`/lesson/${id}`} className="related-topic" key={id}><span>{TOPIC_BY_ID[id]?.name ?? id}</span><ArrowRight size={14} /></Link>) : <p className="muted small">This is a foundation topic.</p>}<Link to="/gaps" className="text-link related-map-link">View learning map <ArrowRight size={14} /></Link></div><div className="lesson-aside-foot"><span><Headphones size={15} /> {speechSupported ? 'Audio available in this browser' : 'Audio not supported in this browser'}</span><small>{MOCK_MODE ? 'Lesson content is demo seed content.' : 'Lesson supplied by the connected backend.'}</small></div></aside>
      </div>
    </>}
  </div>;
}
