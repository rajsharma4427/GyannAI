import { useEffect, useState } from 'react';
import { ArrowUpRight, BookOpen, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Topic, TopicState } from '../api/types';
import { TOPIC_BY_ID } from '../data/topics';
import { MasteryBar } from './MasteryBar';
import { StatusBadge } from './StatusBadge';
import { NotesPanel } from './NotesPanel';

export function TopicDrawer({ topic, state, allStates, studentId, onClose }: {
  topic: Topic | null; state?: TopicState; allStates: TopicState[]; studentId: string; onClose: () => void;
}) {
  const [visible, setVisible] = useState(false);
  useEffect(() => { setVisible(Boolean(topic)); }, [topic]);
  useEffect(() => {
    if (!topic) return;
    const onKey = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [topic, onClose]);
  if (!topic || !visible) return null;
  const prereqs = topic.prereq_ids.map((id) => TOPIC_BY_ID[id]).filter((item): item is NonNullable<typeof item> => Boolean(item));
  const statusFor = (id: string) => allStates.find((item) => item.topic_id === id);
  return <div className="drawer-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <aside className="topic-drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      <div className="drawer-top"><span className="eyebrow">TOPIC DETAILS</span><button className="icon-button" aria-label="Close topic details" onClick={onClose}><X size={19} /></button></div>
      <div className="drawer-heading"><div><h2 id="drawer-title">{topic.name}</h2><p>{topic.description}</p></div><StatusBadge status={state?.status ?? 'unseen'} /></div>
      <div className="drawer-mastery"><MasteryBar value={state?.mastery ?? 0} label="Current mastery" /><p className="muted tiny">{state?.status === 'gap' ? `Gap type: ${state.gap_type ?? 'under review'}` : state?.status === 'unseen' ? 'No learning history recorded for this topic.' : 'Based on available demo or backend progress.'}</p></div>
      <section className="drawer-section"><h3>Builds on</h3>{prereqs.length ? <div className="prereq-list">{prereqs.map((prereq) => <div className="prereq-row" key={prereq.id}><span className={`prereq-marker status-${statusFor(prereq.id)?.status ?? 'unseen'}`} /><span>{prereq.name}</span><span className="muted tiny">{Math.round((statusFor(prereq.id)?.mastery ?? 0) * 100)}%</span></div>)}</div> : <p className="muted small">This is a foundation topic with no listed prerequisites.</p>}</section>
      <div className="drawer-actions"><Link className="button button-primary" to={`/lesson/${topic.id}`} onClick={onClose}><BookOpen size={16} /> Study lesson</Link><Link className="button button-secondary" to={`/diagnostic/${topic.id}`} onClick={onClose}>Practice topic <ArrowUpRight size={16} /></Link></div>
      <NotesPanel studentId={studentId} topicId={topic.id} />
    </aside>
  </div>;
}
