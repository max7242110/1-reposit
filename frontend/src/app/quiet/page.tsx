import type { Metadata } from "next";
import BackLink from "@/components/BackLink";
import RatingTableV2 from "@/components/RatingTableV2";
import { getModels } from "@/lib/api";
import { getRatingYear } from "@/lib/year";

export const revalidate = 86400;

export function generateMetadata(): Metadata {
  const year = getRatingYear();
  return {
    title: `Самые тихие кондиционеры — рейтинг ${year}`,
    description: `Рейтинг самых тихих бытовых кондиционеров ${year} года по результатам реальных измерений уровня шума.`,
    alternates: { canonical: "/quiet" },
    robots: { index: true, follow: true },
    openGraph: {
      title: `Самые тихие кондиционеры — рейтинг ${year}`,
      description: "Сортировка по измеренному уровню шума. Независимые лабораторные тесты.",
      url: "/quiet",
    },
  };
}

export default async function QuietPage() {
  const all = await getModels();
  const models = all
    .filter((m) => m.has_noise_measurement)
    .sort((a, b) => (b.noise_score ?? 0) - (a.noise_score ?? 0));

  const year = getRatingYear();

  return (
    <>
      <BackLink href="/" />

      <section className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Самые тихие кондиционеры
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Рейтинг {year} года: модели с реально измеренным уровнем шума, отсортированные
          по итоговому баллу «шумности» (чем выше — тем тише).
        </p>
      </section>

      {models.length > 0 ? (
        <RatingTableV2 models={models} indexMode="noise" />
      ) : (
        <p className="text-center text-gray-500 dark:text-gray-400 py-12">
          Пока нет моделей с измеренным уровнем шума.
        </p>
      )}
    </>
  );
}
