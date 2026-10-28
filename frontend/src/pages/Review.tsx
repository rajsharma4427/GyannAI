import { useEffect, useState } from 'react';
import { ArrowLeft, ArrowRight, RotateCcw, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { Flashcard, TopicState } from '../api/types';
import { TOPIC_BY_ID } from '../data/topics';
import { useAppStore } from '../store/useApp';
import { addActivity } from '../utils/activity';
import { PageHeader } from '../components/PageHeader';
import { ErrorState, LoadingState } from '../components/StateMessage';

const ratings = [{ label: 'Again', quality: 1, hint: 'Need another look' }, { label: 'Hard', quality: 3, hint: 'Took effort' }, { label: 'Good', quality: 4, hint: 'Felt clear' }, { label: 'Easy', quality: 5, hint: 'Felt simple' }];

export function ReviewPage() {
  const { studentId } = useAppStore();
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [index, setIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [reviewed, setReviewed] = useState<Record<string, number>>({});
  const [lastState, setLastState] = useState<TopicState | null>(null);
  const [ratingBusy, setRatingBusy] = useState(false);
  const load = async () => { setLoading(true); setError(''); try { setCards((await api.getDueCards(studentId)).cards); setIndex(0); setRevealed(false); setReviewed({}); setLastState(null); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Flashcards could not be loaded.'); } finally { setLoading(false); } };
  useEffect(() => { void load(); }, [studentId]);
  const card = cards[index];
  const move = (direction: number) => { setIndex((current) => Math.max(0, Math.min(cards.length - 1, current + direction))); setRevealed(false); setLastState(null); };
  const rate = async (quality: number) => {
    if (!card || ratingBusy) return;
    setRatingBusy(true); setError('');
    try { const result = await api.reviewCard({ student_id: studentId, card_id: card.id, quality }); setReviewed((current) => ({ ...current, [card.id]: quality })); setLastState(result.state); addActivity('Reviewed a flashcard', TOPIC_BY_ID[card.topic_id]?.name ?? card.topic_id); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Your rating could not be saved.'); }
    finally { setRatingBusy(false); }
  };

  return <div className="page-stack">
    <PageHeader eyebrow="KEEP THE IDEA FRESH" title="A little review goes a long way." description="Turn the tricky parts into small prompts you can revisit. Reveal first, then rate how it felt." action={<span className="header-count">{cards.length ? `${index + 1} of ${cards.length}` : 'Revision deck'}</span>} />
    {loading ? <LoadingState label="Loading your revision cards…" /> : error && !cards.length ? <ErrorState message={error} onRetry={() => void load()} /> : !cards.length ? <section className="empty-state review-empty"><span className="empty-icon"><Sparkles size={22} /></span><h2>No cards are due right now.</h2><p>When a learning gap or teach-back creates revision cards, they’ll appear here.</p><Link className="button button-primary" to="/teach-back/quadratic_equations">Create cards with teach-back <ArrowRight size={15} /></Link></section> : <div className="review-layout"><section className="review-main"><div className="review-progress-row"><span className="eyebrow">YOUR REVISION DECK</span><span className="muted small">{Object.keys(reviewed).length} reviewed this session</span></div><div className={`flashcard ${revealed ? 'flashcard-revealed' : ''}`}><div className="flashcard-top"><span className="flashcard-type">{card.source === 'gap' ? 'From a learning gap' : 'From teach-back'}</span><span className="flashcard-topic">{TOPIC_BY_ID[card.topic_id]?.name ?? card.topic_id}</span></div><div className="flashcard-content">{revealed ? <><span className="eyebrow">THE KEY IDEA</span><p>{card.back}</p></> : <><span className="eyebrow">THINK IT THROUGH</span><h2>{card.front}</h2><p className="muted small">Pause for a moment and try to answer before revealing.</p></>}</div><button className="flashcard-reveal-button" onClick={() => setRevealed((current) => !current)}><RotateCcw size={16} /> {revealed ? 'Show question' : 'Reveal answer'}</button><div className="flashcard-bottom"><span>Card {index + 1}</span><div className="flashcard-dots">{cards.map((item, cardIndex) => <button key={item.id} aria-label={`Go to card ${cardIndex + 1}`} className={`${cardIndex === index ? 'flashcard-dot-active' : ''} ${reviewed[item.id] ? 'flashcard-dot-reviewed' : ''}`} onClick={() => { setIndex(cardIndex); setRevealed(false); setLastState(null); }} />)}</div><span>{Math.round(((index + 1) / cards.length) * 100)}%</span></div></div>
      {revealed && <section className="rating-panel"><div><h3>How did that feel?</h3><p>Choose honestly. This helps the review system plan what to revisit.</p></div><div className="rating-buttons">{ratings.map((rating) => <button key={rating.quality} className={`rating-button ${reviewed[card.id] === rating.quality ? 'rating-selected' : ''}`} onClick={() => void rate(rating.quality)} disabled={ratingBusy}><strong>{rating.label}</strong><small>{rating.hint}</small></button>)}</div>{lastState && <p className="review-saved" role="status">Rating saved. Current review interval: {lastState.interval_days} day{lastState.interval_days === 1 ? '' : 's'}. {lastState.next_review ? `Next review: ${lastState.next_review}.` : ''}</p>}{error && <p className="inline-error" role="alert">{error}</p>}</section>}
      <div className="review-navigation"><button className="button button-secondary" onClick={() => move(-1)} disabled={index === 0}><ArrowLeft size={15} /> Previous</button><button className="button button-secondary" onClick={() => move(1)} disabled={index === cards.length - 1}>Next card <ArrowRight size={15} /></button></div></section><aside className="review-side"><div className="review-tip-card"><span className="tip-card-icon"><Sparkles size={18} /></span><span className="eyebrow">REVISION TIP</span><h3>Try before you flip.</h3><p>Even a short attempt to retrieve an answer can make revision more useful than simply rereading a solution.</p></div><div className="review-topic-card"><span className="eyebrow">CARD TOPIC</span><h3>{TOPIC_BY_ID[card.topic_id]?.name ?? card.topic_id}</h3><p>{TOPIC_BY_ID[card.topic_id]?.description}</p><Link to={`/lesson/${card.topic_id}`} className="text-link">Revisit its lesson <ArrowRight size={14} /></Link></div></aside></div>}
  </div>;
}
