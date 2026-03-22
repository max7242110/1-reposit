import { Metadata } from "next";
import { notFound } from "next/navigation";

import BackLink from "@/components/BackLink";
import IndexCriterionCard from "@/components/IndexCriterionCard";
import RegionBadges from "@/components/RegionBadges";
import VerificationBadge from "@/components/VerificationBadge";
import VideoLinks from "@/components/VideoLinks";
import { getModel } from "@/lib/api";
import { formatIndexMax } from "@/lib/utils";

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  try {
    const m = await getModel(Number(id));
    const idxLabel = `${m.total_index.toFixed(1)} / ${formatIndexMax(m.index_max ?? 100)}`;
    return {
      title: `${m.brand.name} ${m.inner_unit}`,
      description: `Индекс «Август-климат»: ${idxLabel}. ${m.brand.name} ${m.inner_unit} — подробные параметры и видеообзор.`,
      openGraph: {
        title: `${m.brand.name} ${m.inner_unit} — Рейтинг «Август-климат»`,
        description: `Индекс: ${idxLabel}. Подробные характеристики.`,
      },
    };
  } catch {
    return { title: "Модель не найдена" };
  }
}

export default async function ModelDetailPage({ params }: Props) {
  const { id } = await params;
  let model;
  try {
    model = await getModel(Number(id));
  } catch {
    notFound();
  }

  const indexMax = model.index_max ?? 100;
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: `${model.brand.name} ${model.inner_unit}`,
    brand: { "@type": "Brand", name: model.brand.name },
    description: `Кондиционер ${model.brand.name} ${model.inner_unit}. Индекс «Август-климат»: ${model.total_index.toFixed(1)} / ${formatIndexMax(indexMax)}.`,
    review: {
      "@type": "Review",
      reviewRating: {
        "@type": "Rating",
        ratingValue: model.total_index.toFixed(1),
        bestRating: formatIndexMax(indexMax),
      },
    },
  };

  return (
    <article>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <BackLink href="/" />

      <header className="mb-8">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
              {model.brand.name}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">{model.inner_unit}</p>
            {model.outer_unit && (
              <p className="text-sm text-gray-500 mt-0.5">
                Наружный блок: {model.outer_unit}
              </p>
            )}
            <div className="flex items-center gap-3 mt-3">
              <RegionBadges regions={model.region_availability} />
              {model.methodology_version && (
                <span className="text-xs text-gray-400">Методика v{model.methodology_version}</span>
              )}
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 dark:text-gray-400">Индекс «Август-климат»</div>
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 tabular-nums">
              <span>{model.total_index.toFixed(1)}</span>
              <span className="font-semibold text-blue-500/80 dark:text-blue-300/80"> / </span>
              <span>{formatIndexMax(model.index_max ?? 100)}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <section aria-label="Параметры">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Параметры</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Все критерии, участвующие в расчёте индекса: исходное значение, балл по шкале 0–100 и вклад в итог.
          </p>
          <div className="bg-gray-50 dark:bg-gray-900 rounded-xl px-4 sm:px-5">
            {model.parameter_scores.length > 0 ? (
              model.parameter_scores.map((ps) => (
                <IndexCriterionCard key={ps.criterion_code} criterion={ps} />
              ))
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400 py-8 text-center">
                Нет активной методики или критериев для отображения.
              </p>
            )}
          </div>
        </section>

        <div className="space-y-8">
          <VideoLinks youtube_url={model.youtube_url} rutube_url={model.rutube_url} vk_url={model.vk_url} />

          {model.raw_values.length > 0 && (
            <section aria-label="Источники данных">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Источники данных</h2>
              <div className="space-y-2">
                {model.raw_values.filter((rv) => rv.source).map((rv) => (
                  <div key={rv.criterion_code} className="flex items-center justify-between text-sm py-1.5 border-b border-gray-100 dark:border-gray-800">
                    <span className="text-gray-600 dark:text-gray-400">{rv.criterion_name}</span>
                    <div className="flex items-center gap-2">
                      <VerificationBadge status={rv.verification_status} display={rv.verification_display} />
                      {rv.source_url ? (
                        <a href={rv.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                          {rv.source}
                        </a>
                      ) : (
                        <span className="text-gray-500">{rv.source}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </article>
  );
}
