import { useEffect, useState, type FormEvent } from 'react';
import { MessageSquareText, Plus } from 'lucide-react';
import { api } from '../api/client';
import type { Note } from '../api/types';

export function NotesPanel({ studentId, topicId }: { studentId: string; topicId: string }) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const load = async () => {
    setLoading(true); setError('');
    try { setNotes((await api.getNotes(studentId, topicId)).notes); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Notes are unavailable.'); }
    finally { setLoading(false); }
  };
  useEffect(() => { void load(); }, [studentId, topicId]);
  const save = async (event: FormEvent) => {
    event.preventDefault();
    if (!text.trim()) return;
    setSaving(true); setError('');
    try { const note = await api.createNote({ student_id: studentId, topic_id: topicId, body: text.trim() }); setNotes((current) => [note, ...current]); setText(''); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not save note.'); }
    finally { setSaving(false); }
  };
  return <section className="notes-panel" aria-labelledby="notes-heading">
    <div className="section-title-row"><h3 id="notes-heading"><MessageSquareText size={17} aria-hidden="true" /> Topic notes</h3><span className="muted tiny">{notes.length} saved</span></div>
    {loading ? <p className="muted small">Loading notes…</p> : notes.length ? <div className="note-list">{notes.map((note) => <article className="note-item" key={note.id}><span className={`note-author note-author-${note.author}`}>{note.author === 'ai' ? 'Learning note' : 'Your note'}</span><p>{note.body}</p></article>)}</div> : <p className="muted small">No notes for this topic yet. Save a useful reminder below.</p>}
    <form className="note-form" onSubmit={save}><label className="sr-only" htmlFor="topic-note">Add a note</label><textarea id="topic-note" value={text} onChange={(event) => setText(event.target.value)} rows={2} placeholder="A reminder you want to keep…" /><button className="button button-secondary button-small" type="submit" disabled={saving || !text.trim()}><Plus size={15} aria-hidden="true" /> {saving ? 'Saving…' : 'Add note'}</button></form>
    {error && <p className="inline-error" role="alert">{error}</p>}
  </section>;
}
