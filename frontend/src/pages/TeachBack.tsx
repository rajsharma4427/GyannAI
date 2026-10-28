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
  useEffect(() => { if (speech.transcript) setText(speech.transcript); }, [speech.transcript]);
  useEffect(() => () => { speech.stop(); synthesis.cancel(); }, []);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!text.trim()) { setError('Add a few words about the concept before submitting.'); return; }
    setSubmitting(true); setError('');
    try { const response = await api.submitTeachBack({ student_id: studentId, topic_id: topic.id, transcript: text.trim() }); setResult(response); addActivity('Completed teach-back', topic.name); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Your explanation could not be checked.'); }
    finally { setSubmitting(false); }
  };

  if (result) return <div className="page-stack">
    <PageHeader eyebrow="TEACH-BACK · FEEDBACK" title="You made the idea your own." description="Use this reflection to decide what to practise next. A score is only one small signal." action={<button className="button button-secondary button-small" onClick={() => { setResult(null); setText(''); speech.reset(); }}> <RotateCcw size={15} /> Try again</button>} />
    <section className="teachback-result-panel panel"><div className="result-score"><span className="score-ring"><strong>{Math.round(result.result.score * 100)}<small>%</small></strong></span><div><span className="eyebrow">{MOCK_MODE ? 'DEMO FEEDBACK' : 'YOUR REFLECTION'}</span><h2>Here’s what to build on</h2><p>{result.result.feedback}</p>{MOCK_MODE && <span className="demo-disclaimer">This is deterministic demo feedback, not an AI assessment.</span>}</div></div>
      <div className="feedback-columns"><section className="feedback-list feedback-list-positive"><h3><CheckCircle2 size={17} /> You touched on</h3>{result.result.covered.length ? result.result.covered.map((item) => <p key={item}><CheckCircle2 size={15} />{item}</p>) : <p>No concepts were marked as covered yet.</p>}</section><section className="feedback-list feedback-list-improve"><h3><Sparkles size={17} /> Try adding</h3>{result.result.missing.length ? result.result.missing.map((item) => <p key={item}><span className="feedback-bullet" />{item}</p>) : <p>Nothing specific was flagged.</p>}</section></div>
      <div className="submitted-words"><span className="eyebrow">YOUR EXPLANATION</span><p>{text}</p></div>
      {result.flashcards.length > 0 && <div className="generated-cards"><span className="eyebrow">ADDED TO REVISION</span><div>{result.flashcards.map((card) => <article key={card.id}><strong>{card.front}</strong><p>{card.back}</p></article>)}</div></div>}
      <div className="result-actions"><Link className="button button-primary" to="/review">Review flashcards <ArrowRight size={16} /></Link><Link className="button button-secondary" to={`/lesson/${topic.id}`}>Revisit lesson</Link></div>
    </section>
  </div>;

  return <div className="page-stack">
    <PageHeader eyebrow="TEACH IT BACK" title="Explain it in your own words." description={`Tell us how you understand ${topic.name.toLowerCase()}. It doesn't need to sound like a textbook.`} action={<Link className="button button-secondary button-small" to={`/lesson/${topic.id}`}><ArrowRight size={15} /> Revisit lesson</Link>} />
    <div className="teachback-layout"><section className="teachback-main panel"><div className="teachback-prompt"><span className="teachback-prompt-icon"><Sparkles size={20} /></span><div><span className="eyebrow">A GENTLE PROMPT</span><h2>How would you explain this to a friend?</h2><p>What is the main idea? Which steps matter? Can you add a small example?</p></div></div>
      <div className="voice-recorder"><div className={`mic-visual ${speech.listening ? 'mic-listening' : ''}`}><span className="mic-ripple" /><span className="mic-core"><Mic size={25} /></span></div><div className="voice-recorder-copy"><strong>{speech.listening ? 'Listening to your explanation…' : speech.supported ? 'Speak your explanation' : 'Voice input isn’t available here'}</strong><p>{speech.listening ? 'Speak naturally. Stop when you have said enough.' : speech.supported ? 'Use the microphone, or type below instead.' : 'No problem—typing works just as well.'}</p></div>{speech.supported && (speech.listening ? <button className="button button-danger" onClick={() => speech.stop()}><MicOff size={16} /> Stop recording</button> : <button className="button button-primary" onClick={() => { speech.reset(); setText(''); setError(''); speech.start(); }}><Mic size={16} /> Start speaking</button>)}</div>
      {speech.supported && <div className="transcript-status" role="status"><span className={`recording-indicator ${speech.listening ? 'recording-indicator-on' : ''}`} />{speech.listening ? 'Microphone active · transcript appears below' : 'Microphone ready'}{speech.interim && <em> “{speech.interim}”</em>}</div>}
      <form onSubmit={submit} className="teachback-form"><label htmlFor="teachback-text">Your explanation</label><textarea id="teachback-text" value={text} onChange={(event) => setText(event.target.value)} rows={7} placeholder="For example: Factorization means finding two expressions that multiply to make the original expression…" /><div className="form-footer"><span className="muted tiny">{text.trim() ? text.trim().split(/\s+/).length : 0} words · Edit the transcript before submitting</span><button className="button button-primary" type="submit" disabled={submitting || !text.trim()}>{submitting ? 'Reflecting…' : 'Submit explanation'} <Send size={16} /></button></div>{error && <p className="inline-error" role="alert">{error}</p>}</form>
      <div className="privacy-note"><CheckCircle2 size={15} /><span>Your words are used for this learning activity. In mock mode, feedback is generated with a small deterministic rule set.</span></div>
    </section><aside className="teachback-aside"><div className="aside-tip-card"><span className="eyebrow">A HELPFUL STRUCTURE</span><h3>Three parts are enough.</h3><div className="tip-step"><span>1</span><div><strong>The idea</strong><p>Say what the concept means.</p></div></div><div className="tip-step"><span>2</span><div><strong>The process</strong><p>Describe one or two key steps.</p></div></div><div className="tip-step"><span>3</span><div><strong>An example</strong><p>Use a small number or expression.</p></div></div><button className="button button-secondary button-block" onClick={() => synthesis.speak(`The main idea of ${topic.name} is this. Explain the rule in your own words, then show one small example.`)} disabled={!synthesis.supported}><Volume2 size={16} /> Hear the prompt</button></div><div className="aside-tip-small"><strong>There’s no perfect wording.</strong><p>The goal is to notice what feels clear and what deserves another look.</p></div></aside></div>
  </div>;
}
