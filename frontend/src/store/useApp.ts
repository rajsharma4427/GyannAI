import { create } from 'zustand';
import type { Lang } from '../api/types';
import { DEMO_PROFILES } from '../data/demo';

interface AppState {
  studentId: string;
  studentName: string;
  lang: Lang;
  setStudentId: (studentId: string, studentName?: string) => void;
  setLang: (lang: Lang) => void;
}
function readString(key: string, fallback: string) {
  try { return localStorage.getItem(key) || fallback; } catch { return fallback; }
}
function nameForStudent(studentId: string) {
  return DEMO_PROFILES.find((profile) => profile.student_id === studentId)?.name ?? readString('gyaan-loop-student-name', 'Your learner profile');
}
export const useAppStore = create<AppState>((set) => ({
  studentId: readString('gyaan-loop-student-id', 'demo_learner_gaps'),
  studentName: readString('gyaan-loop-student-name', 'Aarav Sharma'),
  lang: (readString('gyaan-loop-lang', 'en') as Lang),
  setStudentId: (studentId, studentName) => {
    const resolvedName = studentName ?? nameForStudent(studentId);
    try {
      localStorage.setItem('gyaan-loop-student-id', studentId);
      localStorage.setItem('gyaan-loop-student-name', resolvedName);
    } catch { /* private browsing can disable storage */ }
    set({ studentId, studentName: resolvedName });
  },
  setLang: (lang) => {
    try { localStorage.setItem('gyaan-loop-lang', lang); } catch { /* private browsing can disable storage */ }
    set({ lang });
  },
}));
