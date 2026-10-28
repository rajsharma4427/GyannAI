export interface ActivityItem { id: string; label: string; detail: string; at: string; }
const STORAGE_KEY = 'gyaan-loop-activity';
export function addActivity(label: string, detail: string) {
  const item: ActivityItem = { id: `${Date.now()}-${Math.random().toString(36).slice(2, 6)}`, label, detail, at: new Date().toISOString() };
  try {
    const existing = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') as ActivityItem[];
    localStorage.setItem(STORAGE_KEY, JSON.stringify([item, ...existing].slice(0, 12)));
  } catch { /* activity history is optional if storage is unavailable */ }
}
export function getActivity(): ActivityItem[] {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') as ActivityItem[]; }
  catch { return []; }
}
