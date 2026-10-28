import { useState, type FormEvent } from 'react';
import { ArrowRight, CheckCircle2, GraduationCap, Sparkles, UserRound } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api, MOCK_MODE } from '../api/client';
import type { Lang } from '../api/types';
import { DEMO_PROFILES } from '../data/demo';
import { useAppStore } from '../store/useApp';
import { PageHeader } from '../components/PageHeader';

export function SetupPage() {
  const { setStudentId, lang: savedLang, setLang } = useAppStore();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [lang, setSelectedLang] = useState<Lang>(savedLang);
  const [goal, setGoal] = useState('Build confidence with quadratic equations');
  const [syllabus, setSyllabus] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const switchDemo = (studentId: string) => { setStudentId(studentId); setSuccess('Demo learner selected.'); setError(''); window.setTimeout(() => navigate('/'), 250); };
  const createProfile = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true); setError(''); setSuccess('');
    try {
      const created = await api.createStudent({ name: name.trim(), lang });
      if (goal.trim() || syllabus.trim()) await api.createSyllabus({ student_id: created.student_id, ...(syllabus.trim() ? { text: syllabus.trim() } : { goal: goal.trim() }) });
      setStudentId(created.student_id, name.trim()); setLang(lang); setSuccess('Your learner space is ready.');
      window.setTimeout(() => navigate('/'), 300);
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'The learner profile could not be created.'); }
    finally { setBusy(false); }
  };
  return <div className="page-stack setup-page"><PageHeader eyebrow="MAKE IT YOURS" title="A learning space that starts with you." description="Choose a demonstration profile or set up a learner. No account or paid service is required for the local demo." />
    <div className="setup-columns"><section className="setup-demo-section"><div className="setup-section-heading"><span className="setup-step-number">01</span><div><h2>Try a demo learner</h2><p>Switch between two prepared starting points to see how the experience changes.</p></div></div><div className="demo-profile-list">{DEMO_PROFILES.map((profile) => <button key={profile.student_id} className="demo-profile-card" onClick={() => switchDemo(profile.student_id)}><span className={`demo-profile-avatar ${profile.kind === 'new' ? 'new-profile-avatar' : ''}`}>{profile.kind === 'new' ? <Sparkles size={20} /> : profile.name.split(' ').map((word) => word[0]).slice(0, 2).join('')}</span><span className="demo-profile-details"><strong>{profile.name}</strong><span>{profile.description}</span><em>{profile.kind === 'new' ? 'All topics not started' : 'Focus on factorization and linear equations'}</em></span><ArrowRight size={17} /></button>)}</div><div className="setup-info-note"><CheckCircle2 size={16} /><p>Demo profiles use deterministic sample data. They are not real students, and their progress is not a real-world impact metric.</p></div></section>
      <section className="setup-form-section"><div className="setup-section-heading"><span className="setup-step-number">02</span><div><h2>Create a learner profile</h2><p>Personalise the welcome and choose a starting goal.</p></div></div><form onSubmit={createProfile} className="setup-form"><div className="form-field"><label htmlFor="learner-name">Student name</label><div className="input-with-icon"><UserRound size={17} /><input id="learner-name" value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Priya" required minLength={2} maxLength={60} /></div></div><div className="form-field"><label htmlFor="learner-lang">Preferred learning language</label><select id="learner-lang" value={lang} onChange={(event) => setSelectedLang(event.target.value as Lang)}><option value="en">English</option><option value="hi">हिन्दी</option><option value="hinglish">Hinglish</option></select></div><div className="form-field"><label htmlFor="learning-goal">Learning goal <span className="field-optional">or</span></label><input id="learning-goal" value={goal} onChange={(event) => setGoal(event.target.value)} placeholder="e.g. Understand quadratic equations" maxLength={240} /></div><div className="form-field"><label htmlFor="syllabus-text">Paste syllabus (optional)</label><textarea id="syllabus-text" value={syllabus} onChange={(event) => setSyllabus(event.target.value)} rows={3} placeholder="Paste a short syllabus or leave this blank to use your goal." /></div><div className="setup-form-note"><GraduationCap size={17} /><span>{MOCK_MODE ? 'Mock mode uses the shared 13-topic Class 10 track.' : 'Your syllabus will be sent to the connected backend.'}</span></div>{error && <p className="inline-error" role="alert">{error}</p>}{success && <p className="inline-success" role="status">{success}</p>}<button type="submit" className="button button-primary button-block" disabled={busy}>{busy ? 'Setting up…' : 'Create learning space'} <ArrowRight size={16} /></button></form></section></div><div className="setup-footnote">This MVP stores the current learner ID and language in this browser only. The backend remains the source of truth when connected.</div>
  </div>;
}
