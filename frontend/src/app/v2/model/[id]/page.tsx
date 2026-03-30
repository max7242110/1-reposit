import { Metadata } from "next";
import { notFound } from "next/navigation";

import BackLink from "@/components/BackLink";
import IndexCriterionCard from "@/components/IndexCriterionCard";
import PhotoGallery from "@/components/PhotoGallery";
import ProsConsBlock from "@/components/ProsConsBlock";
import SupplierLinks from "@/components/SupplierLinks";
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
  const hasVideo = model.youtube_url || model.rutube_url || model.vk_url;

  const sortedScores = [...model.parameter_scores].sort(
    (a, b) => b.normalized_score - a.normalized_score,
  );

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
            {model.series && (
              <p className="text-base font-semibold text-gray-700 dark:text-gray-300 mt-1">
                Серия: {model.series}
              </p>
            )}
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Внутренний блок: {model.inner_unit}
            </p>
            {model.outer_unit && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                Наружный блок: {model.outer_unit}
              </p>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 dark:text-gray-400">Индекс «Август-климат»</div>
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 tabular-nums">
              <span>{model.total_index.toFixed(1)}</span>
              <span className="font-semibold text-blue-500/80 dark:text-blue-300/80"> / </span>
              <span>{formatIndexMax(model.index_max ?? 100)}</span>
            </div>
            {model.price && (
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Рекомендованная цена:{" "}
                <span className="font-semibold text-gray-800 dark:text-gray-200">
                  {new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(
                    parseFloat(model.price),
                  )}{" "}
                  ₽
                </span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <section aria-label="Параметры">
          <div className="bg-gray-50 dark:bg-gray-900 rounded-xl px-4 sm:px-5">
            {sortedScores.length > 0 ? (
              sortedScores.map((ps) => (
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
          <PhotoGallery photos={model.photos} />

          {hasVideo && (
            <VideoLinks youtube_url={model.youtube_url} rutube_url={model.rutube_url} vk_url={model.vk_url} />
          )}

          <ProsConsBlock prosText={model.pros_text} consText={model.cons_text} />

          <SupplierLinks suppliers={model.suppliers} />
        </div>
      </div>
    </article>
  );
}
