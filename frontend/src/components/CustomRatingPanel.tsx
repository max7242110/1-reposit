"use client";

import { CriterionInfo } from "@/lib/types";

interface Props {
  criteria: CriterionInfo[];
  enabled: Record<string, boolean>;
  onChange: (code: string, value: boolean) => void;
  onReset: () => void;
}

export default function CustomRatingPanel({ criteria, enabled, onChange, onReset }: Props) {
  const publicCriteria = criteria.filter((c) => c.is_public);
  const enabledCount = publicCriteria.filter((c) => enabled[c.code] !== false).length;

  return (
    <div className="mb-6 rounded-xl border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 p-4">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-blue-800 dark:text-blue-300">
          Выберите критерии для ранжирования ({enabledCount} из {publicCriteria.length})
        </p>
        <button
          onClick={onReset}
          className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
        >
          Сбросить к умолчанию
        </button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-1.5 max-h-64 overflow-y-auto pr-1">
        {publicCriteria.map((c) => {
          const isEnabled = enabled[c.code] !== false;
          return (
            <label
              key={c.code}
              className="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-800/40 transition-colors"
            >
              <input
                type="checkbox"
                checked={isEnabled}
                onChange={(e) => onChange(c.code, e.target.checked)}
                className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-xs text-gray-700 dark:text-gray-300 leading-tight">
                {c.name_ru}
                <span className="text-gray-400 ml-1">({c.weight}%)</span>
              </span>
            </label>
          );
        })}
      </div>
    </div>
  );
}
