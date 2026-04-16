import { Metadata } from "next";

import BackLink from "@/components/BackLink";
import { getMethodology } from "@/lib/api";
import { CriterionInfo } from "@/lib/types";

export const metadata: Metadata = {
  title: "Методика рейтинга",
  description:
    "Как рассчитывается рейтинг кондиционеров «Август-климат»: описание каждого критерия, веса, шкалы оценки.",
  alternates: { canonical: "/methodology" },
  robots: { index: true, follow: true },
};

export const revalidate = 86400;

const SCORING_LABELS: Record<string, string> = {
  min_median_max: "Линейная шкала (min / медиана / max)",
  binary: "Есть / Нет",
  universal_scale: "Универсальная шкала",
  custom_scale: "Индивидуальная шкала",
  formula: "Расчёт по формуле",
  interval: "Интервальная шкала",
};

const VALUE_TYPE_LABELS: Record<string, string> = {
  numeric: "Числовой",
  binary: "Бинарный",
  categorical: "Категориальный",
  custom_scale: "Индивидуальная шкала",
  formula: "Формула",
  lab: "Лабораторный",
  fallback: "С fallback-логикой",
  brand_age: "Возраст бренда",
};

function WeightBadge({ weight }: { weight: number }) {
  return (
    <span className="inline-flex items-center rounded-full bg-blue-100 dark:bg-blue-900/40 px-2.5 py-0.5 text-xs font-semibold text-blue-700 dark:text-blue-300">
      {weight}%
    </span>
  );
}

function ScaleInfo({ criterion }: { criterion: CriterionInfo }) {
  const parts: string[] = [];

  const scoringLabel = SCORING_LABELS[criterion.scoring_type];
  if (scoringLabel) parts.push(scoringLabel);

  if (criterion.unit) parts.push(`Ед. изм.: ${criterion.unit}`);

  if (criterion.min_value !== null && criterion.max_value !== null) {
    let range = `Диапазон: ${criterion.min_value} — ${criterion.max_value}`;
    if (criterion.median_value !== null) {
      range += `, медиана: ${criterion.median_value}`;
    }
    parts.push(range);
  }

  if (parts.length === 0) return null;

  return (
    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500 dark:text-gray-400">
      {parts.map((part, i) => (
        <span key={i}>{part}</span>
      ))}
    </div>
  );
}

function CriterionCard({ criterion }: { criterion: CriterionInfo }) {
  const typeLabel = VALUE_TYPE_LABELS[criterion.value_type] || criterion.value_type;

  return (
    <div className="py-6 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
      <div className="flex gap-5">
        {criterion.photo_url && (
          <div className="shrink-0">
            <img
              src={criterion.photo_url}
              alt={criterion.name_ru}
              loading="lazy"
              className="w-28 h-28 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
            />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {criterion.name_ru}
            </h3>
            <WeightBadge weight={criterion.weight} />
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {typeLabel}
            </span>
          </div>

          {criterion.description_ru && (
            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              {criterion.description_ru}
            </p>
          )}

          <ScaleInfo criterion={criterion} />
        </div>
      </div>
    </div>
  );
}

export default async function MethodologyPage() {
  const methodology = await getMethodology();

  const publicCriteria = methodology.criteria
    .filter((c) => c.is_public)
    .sort((a, b) => a.display_order - b.display_order);

  const totalWeight = publicCriteria.reduce((sum, c) => sum + c.weight, 0);

  return (
    <>
      <BackLink href="/" />

      <section className="mb-10">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">
          Методика рейтинга «{methodology.name}»
        </h1>

        {methodology.description && (
          <div className="text-gray-600 dark:text-gray-400 leading-relaxed whitespace-pre-line mb-6">
            {methodology.description}
          </div>
        )}

        <div className="flex gap-6 text-sm text-gray-500 dark:text-gray-400">
          <span>
            Критериев:{" "}
            <span className="font-semibold text-gray-700 dark:text-gray-300">
              {publicCriteria.length}
            </span>
          </span>
          <span>
            Сумма весов:{" "}
            <span className="font-semibold text-gray-700 dark:text-gray-300">
              {totalWeight.toFixed(1)}%
            </span>
          </span>
          <span>
            Версия:{" "}
            <span className="font-semibold text-gray-700 dark:text-gray-300">
              {methodology.version}
            </span>
          </span>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Критерии оценки
        </h2>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {publicCriteria.map((criterion) => (
            <CriterionCard key={criterion.code} criterion={criterion} />
          ))}
        </div>
      </section>
    </>
  );
}
