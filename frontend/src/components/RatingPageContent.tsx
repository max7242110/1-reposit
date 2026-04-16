"use client";

import Link from "next/link";
import { Suspense, useEffect, useMemo, useState } from "react";
import CustomRatingPanel from "@/components/CustomRatingPanel";
import RatingFilters from "@/components/RatingFilters";
import RatingTableV2 from "@/components/RatingTableV2";
import { ACModelSummary, CriterionInfo, Methodology } from "@/lib/types";

type TabKey = "standard" | "quiet" | "custom";

const STORAGE_KEY = "custom_rating_enabled";

interface Props {
  models: ACModelSummary[];
  methodology: Methodology | null;
  heading?: string;
  intro?: string;
}

function computeCustomIndex(
  model: ACModelSummary,
  criteria: CriterionInfo[],
  enabled: Record<string, boolean>,
): number {
  const publicCriteria = criteria.filter((c) => c.is_public);
  const activeCriteria = publicCriteria.filter((c) => enabled[c.code] !== false);
  if (activeCriteria.length === 0) return 0;
  const totalWeight = activeCriteria.reduce((sum, c) => sum + c.weight, 0);
  if (totalWeight === 0) return 0;
  const score = activeCriteria.reduce((sum, c) => {
    const s = model.scores[c.code] ?? 0;
    return sum + s * c.weight;
  }, 0);
  return Math.round((score / totalWeight) * 10) / 10;
}

export default function RatingPageContent({ models, methodology, heading, intro }: Props) {
  const [activeTab, setActiveTab] = useState<TabKey>("standard");
  const [enabled, setEnabled] = useState<Record<string, boolean>>({});

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) setEnabled(JSON.parse(stored));
    } catch {}
  }, []);

  const handleCriterionToggle = (code: string, value: boolean) => {
    const next = { ...enabled, [code]: value };
    setEnabled(next);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch {}
  };

  const handleReset = () => {
    setEnabled({});
    try { localStorage.removeItem(STORAGE_KEY); } catch {}
  };

  const displayModels = useMemo(() => {
    if (activeTab === "quiet") {
      return [...models]
        .filter((m) => m.has_noise_measurement)
        .sort((a, b) => (b.noise_score ?? 0) - (a.noise_score ?? 0));
    }
    if (activeTab === "custom" && methodology) {
      return [...models].sort(
        (a, b) =>
          computeCustomIndex(b, methodology.criteria, enabled) -
          computeCustomIndex(a, methodology.criteria, enabled),
      );
    }
    return models; // standard — already sorted by total_index from API
  }, [activeTab, models, methodology, enabled]);

  const tabs: { key: TabKey; label: string }[] = [
    { key: "standard", label: "По индексу «Август-климат»" },
    { key: "quiet", label: "Самые тихие" },
    { key: "custom", label: "Пользовательский рейтинг" },
  ];

  const priceBounds = useMemo(() => {
    const prices = models
      .filter((m) => m.price !== null && parseFloat(m.price!) > 0)
      .map((m) => parseFloat(m.price!));
    if (!prices.length) return { min: undefined, max: undefined };
    return {
      min: Math.floor(Math.min(...prices)),
      max: Math.ceil(Math.max(...prices)),
    };
  }, [models]);

  return (
    <>
      <section className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {heading ?? "Рейтинг «Август-климат»"}
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {intro ??
            "Интегральный индекс качества бытовых кондиционеров на основе независимых измерений и анализа параметров."}
        </p>
      </section>

      <Suspense fallback={<div className="text-center text-gray-400 py-4">Загрузка фильтров...</div>}>
        <RatingFilters defaultPriceMin={priceBounds.min} defaultPriceMax={priceBounds.max} />
      </Suspense>

      {/* Табы */}
      <div className="flex gap-1 mb-6 border-b border-gray-200 dark:border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${
              activeTab === tab.key
                ? "bg-white dark:bg-gray-800 border border-b-white dark:border-gray-700 dark:border-b-gray-800 -mb-px text-blue-600 dark:text-blue-400"
                : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Панель пользовательского рейтинга */}
      {activeTab === "custom" && methodology && (
        <CustomRatingPanel
          criteria={methodology.criteria}
          enabled={enabled}
          onChange={handleCriterionToggle}
          onReset={handleReset}
        />
      )}

      {displayModels.length > 0 ? (
        <>
          <RatingTableV2
            models={displayModels}
            indexMode={activeTab === "quiet" ? "noise" : "standard"}
            customIndex={
              activeTab === "custom" && methodology
                ? Object.fromEntries(
                    displayModels.map((m) => [
                      m.id,
                      computeCustomIndex(m, methodology.criteria, enabled),
                    ]),
                  )
                : undefined
            }
          />
          <div className="mt-4 flex justify-end">
            <Link
              href="/submit"
              className="inline-flex items-center px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
            >
              Добавить кондиционер в рейтинг
            </Link>
          </div>
        </>
      ) : (
        <p className="text-center text-gray-500 dark:text-gray-400 py-12">
          Модели не найдены. Попробуйте изменить фильтры.
        </p>
      )}

      {/* Описание для активного таба */}
      {(() => {
        const tabDescription =
          activeTab === "standard" ? methodology?.tab_description_index :
          activeTab === "quiet" ? methodology?.tab_description_quiet :
          activeTab === "custom" ? methodology?.tab_description_custom : "";
        return tabDescription ? (
          <div className="mt-10 p-6 bg-gray-50 dark:bg-gray-900 rounded-xl">
            <div className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-line leading-relaxed">
              {tabDescription}
            </div>
          </div>
        ) : null;
      })()}
    </>
  );
}
