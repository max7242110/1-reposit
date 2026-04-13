import { ParameterScore } from "@/lib/types";
import { formatYears } from "@/lib/utils";
import Tooltip from "./Tooltip";

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
    criterion_note,
    criterion_description,
    compressor_model,
    raw_value,
    unit,
    normalized_score,
    weighted_score,
    above_reference,
  } = criterion;
  const pct = Math.min(Math.max((normalized_score / SCALE_MAX) * 100, 0), 100);
  const rawDisplay = raw_value.trim() ? raw_value : "—";
  const displayValue = unit === "лет" && rawDisplay !== "—" ? formatYears(rawDisplay) : rawDisplay;
  const displayUnit = unit === "лет" ? "" : unit;

  return (
    <div className="py-4 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 leading-snug flex items-center gap-1.5">
            {criterion_name}
            {criterion_description && (
              <Tooltip text={criterion_description}>
                <span className="inline-flex items-center justify-center w-4 h-4 rounded-full border border-gray-400 dark:border-gray-500 text-[10px] font-bold text-gray-400 dark:text-gray-500 cursor-help shrink-0">
                  ?
                </span>
              </Tooltip>
            )}
          </h3>
          {compressor_model ? (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Модель компрессора: {compressor_model}
            </p>
          ) : null}
          {criterion_note ? (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{criterion_note}</p>
          ) : null}
        </div>
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
        {displayUnit ? (
          <span className="text-gray-500 dark:text-gray-400 ml-1">{displayUnit}</span>
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
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Вклад в индекс:{" "}
            <span className="tabular-nums font-medium text-gray-700 dark:text-gray-300">
              {weighted_score.toFixed(2)}
            </span>
          </p>
          <span className="font-semibold text-gray-900 dark:text-gray-100 tabular-nums">
            {normalized_score.toFixed(1)}
            <span className="font-normal text-gray-400 dark:text-gray-500"> / {SCALE_MAX}</span>
          </span>
        </div>
      </div>
    </div>
  );
}
