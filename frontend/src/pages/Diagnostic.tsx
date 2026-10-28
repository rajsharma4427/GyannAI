import { useCallback, useEffect, useRef, useState } from 'react';
import { ArrowDownRight, ArrowRight, CheckCircle2, CircleHelp, RotateCcw, Target, X } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { api, MOCK_MODE } from '../api/client';
import type { DiagnosticAnswerResponse, Question } from '../api/types';
import { TOPIC_BY_ID } from '../data/topics';
import { useAppStore } from '../store/useApp';
import { addActivity } from '../utils/activity';
import { PageHeader } from '../components/PageHeader';
import { ErrorState, LoadingState } from '../components/StateMessage';

export function DiagnosticPage() {
  const { topicId = 'solve_by_factorization' } = useParams();
  const { studentId } = useAppStore();
  const [sessionId, setSessionId] = useState('');
  const [question, setQuestion] = useState<Question | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [answerResult, setAnswerResult] = useState<DiagnosticAnswerResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);
  const [complete, setComplete] = useState(false);
  const questionStartedAt = useRef(0);
  const topic = TOPIC_BY_ID[topicId] ?? TOPIC_BY_ID.solve_by_factorization;

  const start = useCallback(async () => {
    setLoading(true); setError(''); setComplete(false); setAnswerResult(null); setSelectedIndex(null); setStep(1);
    try { const result = await api.startDiagnostic({ student_id: studentId, topic_id: topic.id }); setSessionId(result.session_id); setQuestion(result.question); questionStartedAt.current = performance.now(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'The diagnostic could not start.'); setQuestion(null); }
    finally { setLoading(false); }
  }, [studentId, topic.id]);
  useEffect(() => { void start(); }, [start]);

  const submit = async () => {
    if (!question || selectedIndex === null || !sessionId) return;
    setSubmitting(true); setError('');
    try {
      const result = await api.answerDiagnostic({ session_id: sessionId, question_id: question.id, chosen_index: selectedIndex, time_ms: Math.max(0, Math.round(performance.now() - questionStartedAt.current)) });
      setAnswerResult(result);
      if (result.done) { setComplete(true); addActivity('Diagnostic completed', topic.name); }
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Your answer could not be checked.'); }
    finally { setSubmitting(false); }
  };
  const continueSession = () => {
    if (!answerResult) return;
    if (answerResult.done || !answerResult.next_question) { setComplete(true); addActivity('Diagnostic reviewed', topic.name); return; }
    setQuestion(answerResult.next_question); questionStartedAt.current = performance.now(); setSelectedIndex(null); setAnswerResult(null); setStep((current) => current + 1);
  };

  return <div className="page-stack">
    <PageHeader eyebrow="QUICK DIAGNOSTIC" title="Let’s find the missing step." description={`A short practice loop starting with ${topic.name.toLowerCase()}. Your answer helps decide what to practise next.`} action={<span className="header-count"><CircleHelp size={15} /> About 3 questions</span>} />
    {loading ? <LoadingState label="Preparing your first question…" /> : error && !question ? <ErrorState message={error} onRetry={() => void start()} /> : complete ? <section className="diagnostic-complete panel"><div className="complete-mark"><CheckCircle2 size={28} /></div><span className="eyebrow">SESSION COMPLETE</span><h2>Good work showing up.</h2><p>This short check is a starting point, not a grade. Revisit the topic that felt tricky, then return to your original problem.</p>{answerResult?.summary?.gaps?.length ? <div className="result-gap-list"><strong>Topics marked for review</strong>{answerResult.summary.gaps.map((gap) => <div key={gap.topic_id}><Target size={15} /><span>{TOPIC_BY_ID[gap.topic_id]?.name ?? gap.topic_id}</span><em>{gap.gap_type}</em></div>)}</div> : null}<div className="complete-actions"><Link className="button button-primary" to="/gaps">View learning map <ArrowRight size={16} /></Link><Link className="button button-secondary" to={`/lesson/${topic.id}`}>Study this topic</Link><button className="button button-ghost" onClick={() => void start()}><RotateCcw size={16} /> Try again</button></div><span className="demo-disclaimer">{MOCK_MODE ? 'Demo result from deterministic sample logic.' : 'Results reflect responses returned by the connected backend.'}</span></section> : question ? <div className="diagnostic-layout">
      <section className="question-panel panel"><div className="question-panel-top"><span className="eyebrow">QUESTION {Math.min(step, 3)} OF 3</span><span className="difficulty-label">{question.difficulty === 1 ? 'Warm-up' : question.difficulty === 2 ? 'Practice' : 'Challenge'}</span></div><div className="question-progress"><span style={{ width: `${Math.min(100, ((step - 1) / 3) * 100)}%` }} /></div><div className="question-topic-label">{TOPIC_BY_ID[question.topic_id]?.name ?? question.topic_id}</div><h2 className="question-stem">{question.stem}</h2><p className="question-hint">Choose the answer you think is right. You’ll see feedback after submitting.</p><div className="answer-options" role="group" aria-label="Answer options">{question.options.map((option, index) => {
        const isPicked = selectedIndex === index;
        const isCorrect = answerResult && question.correct_index === index;
        const isWrongPick = answerResult && isPicked && !answerResult.correct;
        return <button key={`${question.id}-${index}`} className={`answer-option ${isPicked ? 'answer-selected' : ''} ${isCorrect ? 'answer-correct' : ''} ${isWrongPick ? 'answer-wrong' : ''}`} onClick={() => !answerResult && setSelectedIndex(index)} disabled={Boolean(answerResult)} aria-pressed={isPicked}><span className="option-letter">{String.fromCharCode(65 + index)}</span><span>{option}</span>{isCorrect && <CheckCircle2 size={17} className="option-feedback-icon" />}{isWrongPick && <X size={17} className="option-feedback-icon" />}</button>;
      })}</div>
        {error && <p className="inline-error" role="alert">{error}</p>}
        {answerResult && <div className={`answer-feedback ${answerResult.correct ? 'feedback-positive' : 'feedback-caution'}`} role="status"><div className="feedback-heading">{answerResult.correct ? <CheckCircle2 size={18} /> : <ArrowDownRight size={18} />}<strong>{answerResult.correct ? 'That’s right.' : 'Not quite—and that’s useful.'}</strong></div><p>{answerResult.correct ? 'Nice work. Keep the reasoning in mind as you move forward.' : `The correct answer is ${question.options[question.correct_index]}. Review the explanation and practise the related prerequisite before trying again.`}</p>{answerResult.backtrace && <div className="backtrace-callout"><span className="backtrace-icon"><Target size={16} /></span><div><strong>Let’s look one step earlier</strong><p>{answerResult.backtrace.reason}</p><span className="backtrace-route">{TOPIC_BY_ID[answerResult.backtrace.from_topic_id]?.name ?? answerResult.backtrace.from_topic_id} <ArrowRight size={13} /> {TOPIC_BY_ID[answerResult.backtrace.to_topic_id]?.name ?? answerResult.backtrace.to_topic_id}</span></div></div>}</div>}
        <div className="question-footer"><span className="muted small">No penalty for learning from a mistake.</span>{!answerResult ? <button className="button button-primary" onClick={() => void submit()} disabled={selectedIndex === null || submitting}>{submitting ? 'Checking…' : 'Submit answer'} <ArrowRight size={16} /></button> : <button className="button button-primary" onClick={continueSession}>{answerResult.done ? 'See summary' : 'Continue'} <ArrowRight size={16} /></button>}</div>
      </section>
      <aside className="diagnostic-side"><div className="side-note panel"><span className="side-note-icon"><Target size={18} /></span><h3>Why a diagnostic?</h3><p>Gyaan Loop looks for the concept behind a difficult step—not only whether the final answer is correct.</p><div className="mini-steps"><span><i>1</i>Try a question</span><span><i>2</i>Check a prerequisite</span><span><i>3</i>Return with confidence</span></div></div><div className="side-note soft-note"><span className="eyebrow">REMEMBER</span><p>Take your time. An honest answer gives you a more useful next step than a guess made to finish quickly.</p></div></aside>
    </div> : <ErrorState message="No question is available for this topic." onRetry={() => void start()} />}
  </div>;
}
