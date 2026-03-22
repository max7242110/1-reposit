import { ParameterScore } from "@/lib/types";

const SCALE_MAX = 100;

function barFillClass(score: number): string {
  if (score >= 67) return "bg-emerald-500 dark:bg-emerald-400";
  if (score >= 34) return "bg-amber-500 dark:bg-amber-400";
  return "bg-rose-500 dark:bg-rose-400";
}

interface Props {
  criterion: ParameterScore;
}

export default function IndexCriterionCard({ criterion }: Props) {
  const {
    criterion_name,
    raw_value,
    unit,
    normalized_score,
    weighted_score,
    above_reference,
  } = criterion;
  const pct = Math.min(Math.max((normalized_score / SCALE_MAX) * 100, 0), 100);
  const displayValue = raw_value.trim() ? raw_value : "—";

  return (
    <div className="py-4 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 leading-snug">
          {criterion_name}
        </h3>
        {above_reference && (
          <span className="shrink-0 text-xs font-medium text-emerald-600 dark:text-emerald-400">
            выше эталона
          </span>
        )}
      </div>

      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
        <span className="text-gray-500 dark:text-gray-500">Значение:</span>{" "}
        <span className="font-medium text-gray-900 dark:text-gray-100 tabular-nums">
          {displayValue}
        </span>
        {unit ? (
          <span className="text-gray-500 dark:text-gray-400 ml-1">{unit}</span>
        ) : null}
      </p>

      <div className="space-y-1.5">
        <div className="flex justify-between text-[10px] uppercase tracking-wide text-gray-400 dark:text-gray-500 px-0.5">
          <span>0</span>
          <span>50</span>
          <span>100</span>
        </div>
        <div
          className="relative w-full h-3 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden shadow-inner"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={SCALE_MAX}
          aria-valuenow={normalized_score}
          aria-label={`${criterion_name}: ${normalized_score.toFixed(1)} баллов из ${SCALE_MAX}`}
        >
          <div
            className={`h-full rounded-full transition-all duration-500 ${barFillClass(normalized_score)}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="flex items-center justify-between text-sm pt-0.5">
          <span className="text-gray-500 dark:text-gray-400">Балл по методике (0–100)</span>
          <span className="font-semibold text-gray-900 dark:text-gray-100 tabular-nums">
            {normalized_score.toFixed(1)}
            <span className="font-normal text-gray-400 dark:text-gray-500"> / {SCALE_MAX}</span>
          </span>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Вклад в индекс:{" "}
          <span className="tabular-nums font-medium text-gray-700 dark:text-gray-300">
            {weighted_score.toFixed(2)}
          </span>
        </p>
      </div>
    </div>
  );
}
