import { Suspense } from "react";
import RatingFilters from "@/components/RatingFilters";
import RatingTableV2 from "@/components/RatingTableV2";
import { getModels } from "@/lib/api";

interface Props {
  searchParams: Promise<{ brand?: string; region?: string }>;
}

export default async function HomePage({ searchParams }: Props) {
  const params = await searchParams;
  const filters: Record<string, string> = {};
  if (params.brand) filters.brand = params.brand;
  if (params.region) filters.region = params.region;

  const models = await getModels(Object.keys(filters).length ? filters : undefined);

  return (
    <>
      <section className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Рейтинг «Август-климат»
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Интегральный индекс качества бытовых кондиционеров на основе независимых измерений и анализа параметров.
        </p>
      </section>

      <Suspense fallback={<div className="text-center text-gray-400 py-4">Загрузка фильтров...</div>}>
        <RatingFilters />
      </Suspense>

      {models.length > 0 ? (
        <RatingTableV2 models={models} />
      ) : (
        <p className="text-center text-gray-500 dark:text-gray-400 py-12">
          Модели не найдены. Попробуйте изменить фильтры.
        </p>
      )}
    </>
  );
}
