import { useCallback, useEffect, useState } from 'react';
import { ArrowRight, BookOpen, CheckCircle2, Clock3, Target, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { DashboardResponse, GraphResponse } from '../api/types';
import { TOPIC_BY_ID } from '../data/topics';
import { useAppStore } from '../store/useApp';
import { getActivity } from '../utils/activity';
import { PageHeader } from '../components/PageHeader';
import { MasteryBar } from '../components/MasteryBar';
import { StatusBadge } from '../components/StatusBadge';
import { ErrorState, LoadingState } from '../components/StateMessage';

export function ProgressPage() {
  const { studentId } = useAppStore();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activity, setActivity] = useState(getActivity());
  const load = useCallback(async () => { setLoading(true); setError(''); try { const [nextDashboard, nextGraph] = await Promise.all([api.getDashboard(studentId), api.getGraph(studentId)]); setDashboard(nextDashboard); setGraph(nextGraph); setActivity(getActivity()); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Progress could not be loaded.'); } finally { setLoading(false); } }, [studentId]);
  useEffect(() => { void load(); }, [load]);
  const exploredStates = graph?.states.filter((state) => state.status !== 'unseen') ?? [];
  const weakStates = graph?.states.filter((state) => state.status === 'gap').sort((a, b) => a.mastery - b.mastery) ?? [];

  return <div className="page-stack"><PageHeader eyebrow="YOUR LEARNING JOURNEY" title="Progress you can understand." description="A simple view of what you’ve explored, where confidence is growing, and what you can do next." action={<Link to="/topics" className="button button-secondary button-small"><BookOpen size={15} /> Explore topics</Link>} />
    {loading ? <LoadingState label="Gathering your progress…" /> : error || !dashboard || !graph ? <ErrorState message={error || 'Progress data is missing.'} onRetry={() => void load()} /> : <>
      <section className="progress-summary-panel"><div className="progress-summary-main"><span className="eyebrow light-eyebrow">A SNAPSHOT, NOT A GRADE</span><h2>Every concept you practise gives you a clearer next step.</h2><p>Use this page as a guide. Mastery reflects the data currently available for this learner, including demo seed values when demo mode is on.</p></div><div className="progress-score"><span>Overall mastery</span><strong>{Math.round(dashboard.overall_mastery * 100)}<small>%</small></strong><div className="progress-score-track"><span style={{ width: `${Math.round(dashboard.overall_mastery * 100)}%` }} /></div></div></section>
      <section className="progress-metrics"><article className="progress-metric"><span className="stat-icon sage-icon"><BookOpen size={18} /></span><span>Topics explored</span><strong>{exploredStates.length}<small> / {graph.topics.length}</small></strong><p>Topics with a recorded state</p></article><article className="progress-metric"><span className="stat-icon green-icon"><CheckCircle2 size={18} /></span><span>Comfortable topics</span><strong>{dashboard.topics_mastered}</strong><p>Marked mastered in current data</p></article><article className="progress-metric"><span className="stat-icon amber-icon"><Target size={18} /></span><span>Focus areas</span><strong>{weakStates.length}</strong><p>Topics that may need another look</p></article><article className="progress-metric"><span className="stat-icon muted-icon"><Clock3 size={18} /></span><span>Cards to revisit</span><strong>{dashboard.due_today}</strong><p>In the available revision deck</p></article></section>
      <div className="progress-columns"><section className="panel progress-topic-panel"><div className="section-title-row"><div><span className="eyebrow">TOPIC STATUS</span><h2>Progress by concept</h2></div><TrendingUp size={19} className="subtle-icon" /></div><div className="progress-topic-list">{graph.states.filter((state) => state.status !== 'unseen').sort((a, b) => a.mastery - b.mastery).slice(0, 7).map((state) => <div className="progress-topic-row" key={state.topic_id}><div className="progress-topic-heading"><span>{TOPIC_BY_ID[state.topic_id]?.name ?? state.topic_id}</span><StatusBadge status={state.status} /></div><MasteryBar value={state.mastery} showValue /><Link to={`/lesson/${state.topic_id}`} className="progress-topic-review">Review <ArrowRight size={13} /></Link></div>)}{!exploredStates.length && <div className="empty-inset"><strong>Your progress starts with one question.</strong><p>Take a diagnostic to create your first learning signals.</p><Link to="/diagnostic/solve_by_factorization" className="text-link">Start diagnostic <ArrowRight size={14} /></Link></div>}</div><p className="progress-data-note">Topics are sorted by current mastery, lowest first. No charted history is shown because the shared API contract does not provide a time series.</p></section>
        <aside className="progress-right-column"><section className="panel activity-panel"><div className="section-title-row"><div><span className="eyebrow">RECENT ACTIVITY</span><h2>What you’ve done</h2></div></div>{activity.length ? <div className="activity-list">{activity.slice(0, 6).map((item) => <div className="activity-item" key={item.id}><span className="activity-marker"><CheckCircle2 size={14} /></span><div><strong>{item.label}</strong><p>{item.detail}</p><time dateTime={item.at}>{new Date(item.at).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</time></div></div>)}</div> : <div className="empty-inset activity-empty"><span className="empty-icon"><Clock3 size={18} /></span><strong>No activity recorded in this browser yet.</strong><p>Try a lesson, diagnostic, or flashcard. Your recent interactions will appear here.</p></div>}</section><section className="next-step-card"><span className="eyebrow">A NEXT STEP</span><h3>{weakStates.length ? 'Revisit your weakest concept' : 'Choose a concept to practise'}</h3><p>{weakStates.length ? `Build confidence with ${TOPIC_BY_ID[weakStates[0].topic_id]?.name ?? weakStates[0].topic_id}, then try the related quadratic question again.` : 'A short diagnostic can help make your starting point clearer.'}</p><Link to={weakStates.length ? `/lesson/${weakStates[0].topic_id}` : '/diagnostic/solve_by_factorization'} className="button button-primary button-block">Continue learning <ArrowRight size={15} /></Link></section></aside>
      </div>
    </>}
  </div>;
}
