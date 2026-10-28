interface MasteryBarProps { value: number; label?: string; showValue?: boolean; }
export function MasteryBar({ value, label, showValue = true }: MasteryBarProps) {
  const percentage = Math.max(0, Math.min(100, Math.round(value * 100)));
  return (
    <div className="mastery-wrap">
      {(label || showValue) && <div className="mastery-label-row">{label && <span>{label}</span>}{showValue && <strong>{percentage}%</strong>}</div>}
      <div className="mastery-track" role="progressbar" aria-label={label || 'Mastery'} aria-valuenow={percentage} aria-valuemin={0} aria-valuemax={100}>
        <span className="mastery-fill" style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}
