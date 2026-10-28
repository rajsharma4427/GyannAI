import { AlertCircle, LoaderCircle } from 'lucide-react';

export function LoadingState({ label = 'Loading your learning space…' }: { label?: string }) {
  return <div className="state-message" role="status"><LoaderCircle className="spin" size={20} aria-hidden="true" /><span>{label}</span></div>;
}
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return <div className="state-message state-error" role="alert"><AlertCircle size={20} aria-hidden="true" /><div><strong>We couldn’t load this right now.</strong><p>{message}</p>{onRetry && <button className="button button-secondary button-small" onClick={onRetry}>Try again</button>}</div></div>;
}
