import { useEffect, useState } from 'react';
import { ArrowRight, CheckCircle2, CircleDashed, Network, Target } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { GraphResponse, Topic, TopicState } from '../api/types';
import { TOPIC_BY_ID } from '../data/topics';
import { useAppStore } from '../store/useApp';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { ErrorState, LoadingState } from '../components/StateMessage';
import { TopicDrawer } from '../components/TopicDrawer';

const focusIds = ['polynomials', 'factorization', 'linear_equations', 'quadratic_equations', 'solve_by_factorization', 'square_roots', 'quadratic_formula', 'discriminant'];
const dependencyLanes = [
  { label: 'Prerequisite foundations', ids: ['polynomials', 'linear_equations', 'square_roots'] },
  { label: 'Core quadratic concepts', ids: ['factorization', 'quadratic_equations', 'quadratic_formula'] },
  { label: 'Solve and interpret', ids: ['solve_by_factorization', 'discriminant'] },
];

export function GapsPage() {
  const { studentId } = useAppStore();
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<Topic | null>(null);
  const load = async () => { setLoading(true); setError(''); try { setGraph(await api.getGraph(studentId)); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Learning map unavailable.'); } finally { setLoading(false); } };
  useEffect(() => { void load(); }, [studentId]);
  const states = graph?.states ?? [];
  const byId = (id: string) => states.find((state) => state.topic_id === id);
  const topicById = (id: string) => graph?.topics.find((topic) => topic.id === id) ?? TOPIC_BY_ID[id];
  const statusLine = (state: TopicState | undefined) => state?.status === 'gap' ? 'May need another look' : state?.status === 'mastered' ? 'Comfortable for now' : state?.status === 'learning' ? 'Building confidence' : 'Not checked yet';
  const renderNode = (id: string) => {
    const topic = topicById(id);
    const state = byId(id);
    const prerequisites = topic.prereq_ids.map((prereqId) => topicById(prereqId)?.name).filter(Boolean);
    return <button className={`dependency-node node-${state?.status ?? 'unseen'}`} key={id} onClick={() => setSelected(topic ?? null)}>
      <span className="dependency-node-top"><span className="node-status-symbol">{state?.status === 'mastered' ? <CheckCircle2 size={15} /> : state?.status === 'gap' ? <Target size={15} /> : <CircleDashed size={15} />}</span><span>{Math.round((state?.mastery ?? 0) * 100)}%</span></span>
      <strong>{topic.name}</strong><small>{statusLine(state)}</small>
      <span className="dependency-prerequisites">{prerequisites.length ? <><b>Needs</b> {prerequisites.join(' + ')}</> : <b>Foundation topic</b>}</span>
    </button>;
  };

  return <div className="page-stack">
    <PageHeader eyebrow="FOLLOW THE MISSING STEP" title="Learning gaps, made visible." description="A mistake can point to an earlier idea that needs practice. This map shows the prerequisite relationships in the shared syllabus." action={<span className="header-count"><Network size={15} /> Prerequisite map</span>} />
    {loading ? <LoadingState label="Mapping prerequisite relationships…" /> : error || !graph ? <ErrorState message={error || 'No graph data returned.'} onRetry={() => void load()} /> : <>
      <section className="map-explainer"><div className="map-explainer-icon"><Target size={21} /></div><div><strong>Start where the learning gets difficult.</strong><p>In the demo path, difficulty solving a quadratic can lead us back to factorization. The connection is based on the syllabus prerequisites—not a diagnosis of every student.</p></div><span className="map-source-note">{graph.topics.length} canonical topics</span></section>
      <div className="graph-layout">
        <section className="graph-panel" aria-label="Prerequisite relationships">
          <div className="graph-panel-heading"><div><span className="eyebrow">QUADRATICS LEARNING PATH</span><h2>Follow the dependencies</h2></div><div className="graph-legend"><span><i className="legend-dot dot-gap" />Needs attention</span><span><i className="legend-dot dot-learning" />In progress</span><span><i className="legend-dot dot-mastered" />Comfortable</span></div></div>
          <div className="dependency-canvas dependency-list-canvas">
            {dependencyLanes.map((lane) => <section className="dependency-lane" key={lane.label}><div className="dependency-lane-label">{lane.label}</div><div className="dependency-lane-nodes">{lane.ids.map(renderNode)}</div></section>)}
            <div className="graph-caption"><span className="caption-line" />Each node lists its direct prerequisite(s) from the shared syllabus. Select a node to inspect its notes and progress.</div>
          </div>
        </section>
        <aside className="path-summary panel"><span className="eyebrow">A USEFUL LEARNING LOOP</span><h2>One concept at a time</h2><ol className="loop-steps"><li><span>01</span><div><strong>Notice the hard step</strong><p>Try a diagnostic question in the topic you are studying.</p></div></li><li><span>02</span><div><strong>Check the prerequisite</strong><p>Review factorization before repeating the quadratic method.</p></div></li><li><span>03</span><div><strong>Return and try again</strong><p>Use a short lesson, then practise the target topic again.</p></div></li></ol><Link className="button button-primary button-block" to="/diagnostic/solve_by_factorization">Try the demo path <ArrowRight size={16} /></Link><p className="small muted map-honesty">This is a deterministic demo path. Live gap identification comes from backend diagnostic responses.</p></aside>
      </div>
      <section className="all-prereqs-section"><div className="section-title-row"><div><span className="eyebrow">FULL SYLLABUS LINKS</span><h2>What each topic builds on</h2></div><span className="muted small">Click any row to inspect it</span></div><div className="prereq-table">{focusIds.map((id) => { const topic = topicById(id); const state = byId(id); return <button className="prereq-table-row" key={id} onClick={() => setSelected(topic ?? null)}><span className={`prereq-marker status-${state?.status ?? 'unseen'}`} /><span className="prereq-row-main"><strong>{topic.name}</strong><small>{topic.prereq_ids.length ? topic.prereq_ids.map((prereq) => topicById(prereq)?.name).join(' · ') : 'Foundation topic'}</small></span><StatusBadge status={state?.status ?? 'unseen'} /><ArrowRight size={15} /></button>; })}</div></section>
    </>}
    <TopicDrawer topic={selected} state={selected ? byId(selected.id) : undefined} allStates={states} studentId={studentId} onClose={() => setSelected(null)} />
  </div>;
}
