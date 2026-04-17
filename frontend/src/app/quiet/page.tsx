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
    description: `Рейтинг самых тихих бытовых кондиционеров и сплит-систем ${year} года по результатам реальных измерений уровня шума.`,
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

      <div className="mt-10 p-6 bg-gray-50 dark:bg-gray-900 rounded-xl">
        <div className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Как определяются самые тихие кондиционеры {year} года
          </h2>
          <p>
            Рейтинг самых тихих кондиционеров (сплит-систем) составлен на основе
            реальных лабораторных измерений уровня шума внутреннего блока. Замеры
            проводятся в собственной лаборатории «Август-климат» на минимальной
            скорости вентилятора в стандартизированных условиях.
          </p>
          <p>
            Важно понимать: измеренные нами значения, как правило, отличаются от
            каталожных данных производителей. Заводские характеристики шума часто
            указываются для идеальных условий и не отражают реальную картину при
            бытовой эксплуатации. Именно поэтому мы проводим независимые замеры —
            чтобы дать объективную оценку того, насколько тихо работает
            сплит-система в реальности.
          </p>
          <p>
            Для оценки используется инвертированная шкала: чем ниже уровень шума,
            тем выше балл. Параметры шкалы: минимум — 28 дБ(А) (максимальный
            балл), медиана — 33 дБ(А), максимум — 46 дБ(А) (минимальный балл).
            Модели с уровнем шума ниже 28 дБ(А) получают наивысшую оценку.
          </p>
          <p>
            В рейтинг попадают только те сплит-системы и кондиционеры, которые
            прошли реальный замер шума в нашей лаборатории. Если вы хотите, чтобы
            ваша модель была включена в рейтинг самых тихих кондиционеров,
            вы можете{" "}
            <a href="/submit" className="text-blue-600 dark:text-blue-400 hover:underline">
              подать заявку
            </a>{" "}
            на тестирование.
          </p>
        </div>
      </div>
    </>
  );
}
