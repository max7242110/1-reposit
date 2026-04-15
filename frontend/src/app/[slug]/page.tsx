import { Metadata } from "next";
import { notFound } from "next/navigation";

import BackLink from "@/components/BackLink";
import CollapsibleParameters from "@/components/CollapsibleParameters";
import PhotoGallery from "@/components/PhotoGallery";
import ProsConsBlock from "@/components/ProsConsBlock";
import ReviewForm from "@/components/ReviewForm";
import ReviewsList from "@/components/ReviewsList";
import SupplierLinks from "@/components/SupplierLinks";
import VideoLinks from "@/components/VideoLinks";
import { getModelBySlug, getReviews } from "@/lib/api";
import { formatIndexMax } from "@/lib/utils";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    const m = await getModelBySlug(slug);
    const idxLabel = `${m.total_index.toFixed(1)} / ${formatIndexMax(m.index_max ?? 100)}`;
    return {
      title: `Кондиционер ${m.brand.name} ${m.inner_unit}`,
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
  const { slug } = await params;
  let model;
  try {
    model = await getModelBySlug(slug);
  } catch {
    notFound();
  }

  const indexMax = model.index_max ?? 100;
  const hasVideo = model.youtube_url || model.rutube_url || model.vk_url;
  const isArchived = model.publish_status === "archived";

  // noise — всегда первым (особый параметр); далее по вкладу в индекс DESC,
  // тай-брейкер — normalized_score DESC.
  const sortedScores = [...model.parameter_scores].sort((a, b) => {
    if (a.criterion_code === "noise") return -1;
    if (b.criterion_code === "noise") return 1;
    return (
      b.weighted_score - a.weighted_score ||
      b.normalized_score - a.normalized_score
    );
  });

  const reviews = await getReviews(model.id).catch(() => []);

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

      {isArchived && (
        <div className="mb-4 px-4 py-2 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-sm font-medium">
          Архивная модель — не участвует в рейтинге
        </div>
      )}

      <header className="mb-8">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-4">
              <span className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-md bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shrink-0">
                {model.brand.logo ? (
                  <img
                    src={model.brand.logo}
                    alt={`Логотип кондиционеров ${model.brand.name}`}
                    className="max-w-[80%] max-h-[80%] object-contain"
                  />
                ) : (
                  <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase">
                    {model.brand.name.slice(0, 2)}
                  </span>
                )}
              </span>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                Кондиционер {model.brand.name}
              </h1>
            </div>
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
            {model.nominal_capacity != null && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                Мощность охлаждения {model.nominal_capacity} Вт
              </p>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {isArchived ? "Последнее значение индекса" : "Индекс «Август-климат»"}
            </div>
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 tabular-nums">
              <span>{model.total_index.toFixed(1)}</span>
              <span className="font-semibold text-blue-500/80 dark:text-blue-300/80"> / </span>
              <span>{formatIndexMax(model.index_max ?? 100)}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-8">
          <PhotoGallery photos={model.photos} />

          {hasVideo && (
            <VideoLinks youtube_url={model.youtube_url} rutube_url={model.rutube_url} vk_url={model.vk_url} />
          )}

          <ProsConsBlock prosText={model.pros_text} consText={model.cons_text} />

          {model.price && (
            <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900 rounded-xl">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Рекомендованная цена:{" "}
                <span className="font-semibold text-lg text-gray-900 dark:text-gray-100">
                  {new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(
                    parseFloat(model.price),
                  )}{" "}
                  ₽
                </span>
              </p>
            </div>
          )}

          <SupplierLinks suppliers={model.suppliers} />
        </div>

        <section aria-label="Параметры">
          <div className="bg-gray-50 dark:bg-gray-900 rounded-xl px-4 sm:px-5">
            {sortedScores.length > 0 ? (
              <CollapsibleParameters scores={sortedScores} />
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400 py-8 text-center">
                Нет активной методики или критериев для отображения.
              </p>
            )}
          </div>
        </section>
      </div>

      <section aria-label="Отзывы" className="mt-12">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Отзывы пользователей
        </h2>
        <ReviewsList reviews={reviews} />
        <ReviewForm modelId={model.id} />
      </section>
    </article>
  );
}
