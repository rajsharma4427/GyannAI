import { useState } from 'react';
import { CalendarClock, Check } from 'lucide-react';
import { api } from '../api/client';
import { useAppStore } from '../store/useApp';

export function DevBar() {
  const { studentId } = useAppStore();
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const advance = async () => {
    setBusy(true); setMessage('');
    try { const result = await api.advanceDays({ student_id: studentId, days: 3 }); setMessage(`Demo date: ${result.new_date}`); }
    catch (cause) { setMessage(cause instanceof Error ? cause.message : 'Could not advance the demo date.'); }
    finally { setBusy(false); }
  };
  return <div className="dev-bar"><span><CalendarClock size={13} /> {message || 'Demo clock'}</span><button onClick={() => void advance()} disabled={busy}>{busy ? 'Advancing…' : 'Advance 3 days'} <Check size={12} /></button></div>;
}
