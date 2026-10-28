import type { TopicState } from '../api/types';

const labels: Record<TopicState['status'], string> = {
  unseen: 'Not started', gap: 'Needs attention', learning: 'In progress', mastered: 'Comfortable',
};
export function StatusBadge({ status }: { status: TopicState['status'] }) {
  return <span className={`status-badge status-${status}`}><span aria-hidden="true" className="status-dot" />{labels[status]}</span>;
}
