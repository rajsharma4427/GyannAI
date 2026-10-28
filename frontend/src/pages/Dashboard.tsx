import { useCallback, useEffect, useState } from 'react';
import { ArrowRight, ArrowUpRight, BookOpen, CheckCircle2, Clock3, Compass, Flame, Lightbulb, Sparkles, Target } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api, MOCK_MODE } from '../api/client';
import type { DashboardResponse, GraphResponse } from '../api/types';
import { DEMO_PROFILES } from '../data/demo';
import { TOPIC_BY_ID } from '../data/topics';
import { useAppStore } from '../store/useApp';
import { MasteryBar } from '../components/MasteryBar';
import { StatusBadge } from '../components/StatusBadge';
import { ErrorState, LoadingState } from '../components/StateMessage';

export function DashboardPage() {
  const { studentId, studentName } = useAppStore();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const profile = DEMO_PROFILES.find((item) => item.student_id === studentId);
  const name = (profile?.name ?? studentName).split(' ')[0] || 'there';
  const isNew = !profile || profile.kind === 'new';
  const load = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const [nextDashboard, nextGraph] = await Promise.all([api.getDashboard(studentId), api.getGraph(studentId)]);
      setDashboard(nextDashboard); setGraph(nextGraph);
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Your dashboard could not be loaded.'); }
    finally { setLoading(false); }
  }, [studentId]);
  useEffect(() => { void load(); }, [load]);

  if (loading) return <LoadingState label="Putting your learning space together…" />;
  if (error || !dashboard || !graph) return <ErrorState message={error || 'No dashboard data was returned.'} onRetry={() => void load()} />;

  const weak = dashboard.weakest.flatMap((item) => { const topic = TOPIC_BY_ID[item.topic_id]; return topic ? [{ ...item, topic }] : []; });
  const recommendedId = isNew ? 'quadratic_equations' : (weak[0]?.topic.id ?? 'factorization');
  const recommendedTopic = TOPIC_BY_ID[recommendedId];
  const recommendedState = graph.states.find((state) => state.topic_id === recommendedId);
  const explored = graph.states.filter((state) => state.status !== 'unseen').length;

  return <div className="page-stack dashboard-page">
    {MOCK_MODE && <div className="demo-notice"><Sparkles size={16} /><span><strong>Demo workspace</strong> · Sample progress is illustrative and stored for this session.</span><Link to="/setup">Switch learner</Link></div>}
    <section className="welcome-panel">
      <div className="welcome-copy"><div className="eyebrow light-eyebrow">YOUR NEXT STEP STARTS HERE</div><h1>{isNew ? `Welcome, ${name}.` : `Welcome back, ${name}.`}</h1><p>{isNew ? 'Start with one small concept. We’ll build your maths track step by step.' : 'You don’t have to master everything at once. Let’s make the next idea feel easier.'}</p><div className="welcome-actions"><Link className="button button-light" to={`/lesson/${recommendedId}`}><BookOpen size={17} /> {isNew ? 'Start learning' : 'Continue learning'} <ArrowRight size={16} /></Link><Link className="welcome-secondary-link" to="/topics">Explore topics <ArrowUpRight size={15} /></Link></div></div>
      <div className="welcome-art" aria-hidden="true"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="orbit-core"><span>∑</span></div><div className="orbit-note note-one">one idea</div><div className="orbit-note note-two">at a time</div><div className="orbit-dot dot-one" /><div className="orbit-dot dot-two" /></div>
    </section>

    <section className="stats-grid" aria-label="Learning overview">
      <article className="stat-card"><span className="stat-icon sage-icon"><Target size={18} /></span><span className="stat-label">Overall mastery</span><strong className="stat-value">{Math.round(dashboard.overall_mastery * 100)}<small>%</small></strong><MasteryBar value={dashboard.overall_mastery} showValue={false} /><span className="stat-foot">Across the topic track</span></article>
      <article className="stat-card"><span className="stat-icon amber-icon"><BookOpen size={18} /></span><span className="stat-label">Topics explored</span><strong className="stat-value">{explored}<small> / {graph.topics.length}</small></strong><span className="stat-foot">A little progress adds up</span></article>
      <article className="stat-card"><span className="stat-icon green-icon"><CheckCircle2 size={18} /></span><span className="stat-label">Comfortable topics</span><strong className="stat-value">{dashboard.topics_mastered}<small> topics</small></strong><span className="stat-foot">Marked mastered by the current data</span></article>
      <article className="stat-card"><span className="stat-icon muted-icon"><Clock3 size={18} /></span><span className="stat-label">Cards to review</span><strong className="stat-value">{dashboard.due_today}<small> cards</small></strong><span className="stat-foot">Keep key ideas fresh</span></article>
    </section>

    <div className="dashboard-columns">
      <section className="panel recommendation-panel">
        <div className="panel-topline"><span className="panel-icon"><Lightbulb size={18} /></span><span className="eyebrow">A GOOD NEXT STEP</span><span className="recommendation-label">Recommended</span></div>
        <h2>{isNew ? 'Build your quadratic foundations' : `Strengthen ${recommendedTopic.name.toLowerCase()}`}</h2>
        <p>{isNew ? 'Begin with the standard form and learn what makes an equation quadratic.' : recommendedId === 'factorization' ? 'Factor pairs are a useful prerequisite for solving quadratics. Spend a few minutes strengthening this skill first.' : `Review the core idea behind ${recommendedTopic.name.toLowerCase()}, then try one short practice question.`}</p>
        {recommendedState && <div className="recommendation-progress"><MasteryBar value={recommendedState.mastery} label="Current comfort" /></div>}
        <div className="panel-action-row"><Link className="button button-primary" to={`/lesson/${recommendedId}`}>Open lesson <ArrowRight size={16} /></Link><Link className="text-link" to={`/diagnostic/${recommendedId}`}>Try a question</Link></div>
      </section>
      <section className="panel focus-panel">
        <div className="section-title-row"><div><div className="eyebrow">YOUR FOCUS AREAS</div><h2>Where to build confidence</h2></div><Link className="icon-link" to="/gaps" aria-label="View learning gaps"><ArrowUpRight size={18} /></Link></div>
        {weak.length ? <div className="weak-list">{weak.slice(0, 3).map(({ topic, mastery }) => {
          const topicState = graph.states.find((state) => state.topic_id === topic.id);
          return <Link to={`/lesson/${topic.id}`} className="weak-item" key={topic.id}><span className="weak-item-mark"><Target size={16} /></span><span className="weak-item-copy"><strong>{topic.name}</strong><span>{Math.round(mastery * 100)}% current mastery</span></span><span className="weak-item-state">{topicState && <StatusBadge status={topicState.status} />}</span><ArrowRight size={16} className="weak-arrow" /></Link>;
        })}</div> : <div className="empty-inset"><span className="empty-icon"><Sparkles size={20} /></span><strong>{isNew ? 'Your map starts here' : 'No focus areas returned'}</strong><p>{isNew ? 'Take a short diagnostic to create a starting point for your learning.' : 'Keep practising to help identify what to work on next.'}</p><Link to="/diagnostic/solve_by_factorization" className="text-link">Start diagnostic <ArrowRight size={14} /></Link></div>}
      </section>
    </div>

    <section className="next-steps-strip"><div className="next-steps-icon"><Compass size={20} /></div><div><strong>Learning works best in small loops.</strong><p>Try a question, revisit the missing step, then explain the idea in your own words.</p></div><div className="next-steps-actions"><Link to="/gaps">See learning map <ArrowRight size={15} /></Link><Link to="/teach-back/quadratic_equations">Try teach-back <ArrowRight size={15} /></Link></div></section>
    {!isNew && <div className="quiet-streak"><Flame size={15} /><span>Demo streak: {dashboard.streak_days} days</span><span className="quiet-divider" />A gentle reminder to return, not a grade.</div>}
  </div>;
}
