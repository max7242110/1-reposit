import { Metadata } from "next";

import BackLink from "@/components/BackLink";
import RatingTableV2 from "@/components/RatingTableV2";
import { getArchivedModels } from "@/lib/api";

export const metadata: Metadata = {
  title: "Архивные модели",
  description: "Модели кондиционеров, выведенные из активного рейтинга «Август-климат».",
};

export default async function ArchivePage() {
  const models = await getArchivedModels();

  return (
    <>
      <BackLink href="/" />

      <section className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Архивные модели
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Модели кондиционеров, которые были протестированы, но выведены из активного рейтинга.
          Последнее измеренное значение индекса сохранено.
        </p>
      </section>

      {models.length > 0 ? (
        <RatingTableV2 models={models} />
      ) : (
        <p className="text-center text-gray-500 dark:text-gray-400 py-12">
          Архивных моделей пока нет.
        </p>
      )}
    </>
  );
}
