import { BrowserRouter, Route, Routes, Link } from 'react-router-dom';
import { ArrowLeft, Compass } from 'lucide-react';
import { AppLayout } from './layouts/AppLayout';
import { DashboardPage } from './pages/Dashboard';
import { TopicsPage } from './pages/Topics';
import { GapsPage } from './pages/Gaps';
import { DiagnosticPage } from './pages/Diagnostic';
import { LessonPage } from './pages/Lesson';
import { TeachBackPage } from './pages/TeachBack';
import { ReviewPage } from './pages/Review';
import { ProgressPage } from './pages/Progress';
import { SetupPage } from './pages/Setup';

function NotFoundPage() {
  return <div className="not-found-page"><span className="not-found-icon"><Compass size={25} /></span><span className="eyebrow">A SMALL DETOUR</span><h1>This page isn’t on your learning map.</h1><p>Head back to your dashboard or explore the maths topic track.</p><div><Link className="button button-primary" to="/"><ArrowLeft size={16} /> Back to overview</Link><Link className="button button-secondary" to="/topics">Explore topics</Link></div></div>;
}

export default function App() {
  return <BrowserRouter><Routes><Route element={<AppLayout />}><Route index element={<DashboardPage />} /><Route path="topics" element={<TopicsPage />} /><Route path="gaps" element={<GapsPage />} /><Route path="diagnostic/:topicId" element={<DiagnosticPage />} /><Route path="lesson/:topicId" element={<LessonPage />} /><Route path="teach-back/:topicId" element={<TeachBackPage />} /><Route path="review" element={<ReviewPage />} /><Route path="progress" element={<ProgressPage />} /><Route path="setup" element={<SetupPage />} /><Route path="*" element={<NotFoundPage />} /></Route></Routes></BrowserRouter>;
}
