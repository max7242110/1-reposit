import { ParameterValue } from "@/lib/types";

interface Props {
  parameter: ParameterValue;
  maxScore: number;
}

export default function ParameterBar({ parameter, maxScore }: Props) {
  const percentage = maxScore > 0 ? (parameter.score / maxScore) * 100 : 0;

  return (
    <div className="py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {parameter.parameter_name}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {parameter.raw_value}
            {parameter.unit ? ` ${parameter.unit}` : ""}
          </span>
          <span className="text-sm font-semibold text-gray-900 dark:text-gray-100 w-14 text-right">
            {parameter.score.toFixed(1)}
          </span>
        </div>
      </div>
      <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2">
        <div
          className="bg-blue-500 dark:bg-blue-400 h-2 rounded-full transition-all duration-500"
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
}
