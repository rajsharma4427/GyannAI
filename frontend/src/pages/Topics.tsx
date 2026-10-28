import { useEffect, useMemo, useState } from 'react';
import { ArrowUpRight, BookOpen, Search, SlidersHorizontal } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { Topic, TopicState } from '../api/types';
import { TOPIC_GROUPS } from '../data/topics';
import { useAppStore } from '../store/useApp';
import { MasteryBar } from '../components/MasteryBar';
import { StatusBadge } from '../components/StatusBadge';
import { PageHeader } from '../components/PageHeader';
import { ErrorState, LoadingState } from '../components/StateMessage';
import { TopicDrawer } from '../components/TopicDrawer';

export function TopicsPage() {
  const { studentId } = useAppStore();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [states, setStates] = useState<TopicState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selected, setSelected] = useState<Topic | null>(null);
  const load = async () => {
    setLoading(true); setError('');
    try { const data = await api.getGraph(studentId); setTopics(data.topics); setStates(data.states); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Topic track could not be loaded.'); }
    finally { setLoading(false); }
  };
  useEffect(() => { void load(); }, [studentId]);
  const byId = useMemo(() => new Map(states.map((state) => [state.topic_id, state])), [states]);
  const filtered = useMemo(() => topics.filter((topic) => {
    const state = byId.get(topic.id);
    const matchesText = `${topic.name} ${topic.description} ${topic.id}`.toLowerCase().includes(query.toLowerCase());
    return matchesText && (statusFilter === 'all' || (state?.status ?? 'unseen') === statusFilter);
  }), [topics, byId, query, statusFilter]);
  const statusName: Record<string, string> = { all: 'All topics', gap: 'Needs attention', learning: 'In progress', mastered: 'Comfortable', unseen: 'Not started' };

  return <div className="page-stack">
    <PageHeader eyebrow="THE CLASS 10 TRACK" title="Maths, one concept at a time." description="Explore the ideas behind each topic, see what they build on, and choose where to begin." action={<span className="header-count">{topics.length || 13} canonical topics</span>} />
    {loading ? <LoadingState label="Loading topic track…" /> : error ? <ErrorState message={error} onRetry={() => void load()} /> : <>
      <div className="explorer-toolbar"><div className="search-field"><Search size={17} /><label className="sr-only" htmlFor="topic-search">Search topics</label><input id="topic-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search a concept, e.g. factorization" /></div><div className="filter-field"><SlidersHorizontal size={16} /><label className="sr-only" htmlFor="topic-filter">Filter by learning status</label><select id="topic-filter" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>{Object.entries(statusName).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div></div>
      {TOPIC_GROUPS.map((group) => {
        const groupTopics = filtered.filter((topic) => (group.ids as readonly string[]).includes(topic.id));
        if (!groupTopics.length) return null;
        return <section className="topic-group" key={group.label}><div className="topic-group-heading"><div><span className="eyebrow">LEARNING CHAPTER</span><h2>{group.label}</h2></div><span className="muted small">{groupTopics.length} concepts</span></div><div className="topic-grid">{groupTopics.map((topic) => {
          const state = byId.get(topic.id);
          return <article className="topic-card" key={topic.id}><div className="topic-card-top"><span className="topic-index">{String(topics.findIndex((item) => item.id === topic.id) + 1).padStart(2, '0')}</span><StatusBadge status={state?.status ?? 'unseen'} /></div><button className="topic-card-title" onClick={() => setSelected(topic)}>{topic.name}<ArrowUpRight size={16} /></button><p>{topic.description}</p><div className="topic-prereqs"><span>Builds on</span>{topic.prereq_ids.length ? topic.prereq_ids.map((id) => <button key={id} onClick={() => setSelected(topics.find((item) => item.id === id) ?? null)}>{topics.find((item) => item.id === id)?.name ?? id}</button>) : <em>Foundation topic</em>}</div><MasteryBar value={state?.mastery ?? 0} label="Mastery" /><div className="topic-card-actions"><Link to={`/lesson/${topic.id}`} className="button button-primary button-small"><BookOpen size={15} /> Study</Link><Link to={`/diagnostic/${topic.id}`} className="topic-practice-link">Practice <ArrowUpRight size={14} /></Link></div></article>;
        })}</div></section>;
      })}
      {!filtered.length && <div className="empty-state"><span className="empty-icon"><Search size={22} /></span><h2>No topics match that search</h2><p>Try a shorter search or change the status filter.</p><button className="button button-secondary" onClick={() => { setQuery(''); setStatusFilter('all'); }}>Clear filters</button></div>}
    </>}
    <TopicDrawer topic={selected} state={selected ? byId.get(selected.id) : undefined} allStates={states} studentId={studentId} onClose={() => setSelected(null)} />
  </div>;
}
