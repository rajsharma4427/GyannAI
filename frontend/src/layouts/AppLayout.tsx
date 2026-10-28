import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { AudioLines, BookMarked, BookOpen, Brain, ChartNoAxesCombined, ChevronDown, CircleHelp, Compass, LayoutDashboard, Network, NotebookPen, Sparkles } from 'lucide-react';
import { useAppStore } from '../store/useApp';
import { DevBar } from '../components/DevBar';
import { DEMO_PROFILES } from '../data/demo';
import { MOCK_MODE } from '../api/client';
import type { Lang } from '../api/types';

const navigation = [
  { label: 'Overview', to: '/', icon: LayoutDashboard, end: true },
  { label: 'Maths topics', to: '/topics', icon: Compass },
  { label: 'Learning gaps', to: '/gaps', icon: Network },
  { label: 'Quick diagnostic', to: '/diagnostic/solve_by_factorization', icon: Brain },
  { label: 'Lessons', to: '/lesson/quadratic_equations', icon: BookOpen },
  { label: 'Teach-back', to: '/teach-back/quadratic_equations', icon: AudioLines },
  { label: 'Flashcard review', to: '/review', icon: BookMarked },
  { label: 'Progress', to: '/progress', icon: ChartNoAxesCombined },
];

export function AppLayout() {
  const { studentId, studentName, setStudentId, lang, setLang } = useAppStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  useEffect(() => { setMobileMenuOpen(false); }, [location.pathname]);
  const currentProfile = DEMO_PROFILES.find((profile) => profile.student_id === studentId);
  const currentName = currentProfile?.name ?? studentName;
  const initials = currentName.split(/\s+/).slice(0, 2).map((word) => word[0]).join('').toUpperCase();

  return <div className="app-shell">
    <header className="mobile-topbar"><button className="brand brand-button" onClick={() => navigate('/')} aria-label="Gyaan Loop home"><span className="brand-mark"><span>g</span><span>↻</span></span><span className="brand-copy"><strong>gyaan loop</strong><small>maths, made clearer</small></span></button><button className="mobile-menu-toggle" aria-expanded={mobileMenuOpen} onClick={() => setMobileMenuOpen((open) => !open)} aria-label="Toggle navigation"><ChevronDown size={18} /></button></header>
    <aside className={`sidebar ${mobileMenuOpen ? 'sidebar-open' : ''}`}>
      <button className="brand" onClick={() => navigate('/')} aria-label="Gyaan Loop home"><span className="brand-mark"><span>g</span><span>↻</span></span><span className="brand-copy"><strong>gyaan loop</strong><small>maths, made clearer</small></span></button>
      <div className="sidebar-kicker">YOUR LEARNING SPACE</div>
      <nav className="side-nav" aria-label="Main navigation">
        {navigation.map(({ label, to, icon: Icon, end }) => <NavLink key={label} to={to} end={end} className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : ''}`}><Icon size={18} strokeWidth={1.8} aria-hidden="true" /><span>{label}</span></NavLink>)}
      </nav>
      <div className="sidebar-bottom">
        <div className="help-card"><span className="help-icon"><Sparkles size={17} /></span><strong>Small steps count.</strong><p>One clear concept can make the next one easier.</p><button onClick={() => navigate('/topics')}>Explore topics <span aria-hidden="true">↗</span></button></div>
        <button className="setup-link" onClick={() => navigate('/setup')}><NotebookPen size={17} /> Set up a learner</button>
        <div className="sidebar-foot"><span className="tiny-brand-mark">G</span><span>Built for curious minds</span></div>
      </div>
    </aside>
    <div className="main-column">
      <header className="topbar">
        <div className="breadcrumb"><span>Learning space</span><span aria-hidden="true">/</span><strong>{navigation.find((item) => item.to === location.pathname)?.label ?? (location.pathname.startsWith('/lesson') ? 'Lesson' : location.pathname.startsWith('/diagnostic') ? 'Diagnostic' : location.pathname.startsWith('/teach-back') ? 'Teach-back' : 'Learn')}</strong></div>
        <div className="topbar-actions">
          {MOCK_MODE && <span className="demo-pill"><span /> Demo mode</span>}
          <label className="sr-only" htmlFor="language-select">Learning language</label><select id="language-select" className="topbar-select language-select" value={lang} onChange={(event) => setLang(event.target.value as Lang)} aria-label="Learning language"><option value="en">English</option><option value="hi">हिन्दी</option><option value="hinglish">Hinglish</option></select>
          <label className="sr-only" htmlFor="student-select">Demo learner</label>
          <select
            id="student-select"
            className="topbar-select student-select"
            value={DEMO_PROFILES.some((profile) => profile.student_id === studentId) ? studentId : 'custom'}
            onChange={(event) => {
              if (event.target.value !== 'custom') {
                const found = DEMO_PROFILES.find((p) => p.student_id === event.target.value);
                setStudentId(event.target.value, found?.name);
              }
            }}
            aria-label="Select learner"
          >
            {DEMO_PROFILES.map((profile) => (
              <option key={profile.student_id} value={profile.student_id}>
                {profile.name} · {profile.kind === 'returning' ? 'returning' : 'new learner'}
              </option>
            ))}
            {!DEMO_PROFILES.some((profile) => profile.student_id === studentId) && <option value="custom">New profile</option>}
          </select>
          <div className="avatar" aria-hidden="true">{initials}</div>
        </div>
      </header>
      <main className="page-content"><Outlet /></main>
      <footer className="app-footer"><span>Gyaan Loop</span><span>Learn the missing step, not just the next answer.</span><div className="app-footer-links">{MOCK_MODE && <DevBar />}<a href="/setup"><CircleHelp size={14} /> Demo setup</a></div></footer>
    </div>
    {mobileMenuOpen && <button className="mobile-menu-dismiss" aria-label="Close navigation menu" onClick={() => setMobileMenuOpen(false)} />}
  </div>;
}
