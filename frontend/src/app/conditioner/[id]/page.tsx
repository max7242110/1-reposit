import { Metadata } from "next";
import { notFound } from "next/navigation";

import BackLink from "@/components/BackLink";
import ParameterBar from "@/components/ParameterBar";
import VideoLinks from "@/components/VideoLinks";
import { getConditioner } from "@/lib/api";

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  try {
    const ac = await getConditioner(Number(id));
    return {
      title: `${ac.brand} ${ac.model_name}`,
      description: `Обзор и рейтинг кондиционера ${ac.brand} ${ac.model_name}. Итоговый балл: ${ac.total_score}. Подробные параметры и видеообзор.`,
      openGraph: {
        title: `${ac.brand} ${ac.model_name} — Рейтинг кондиционеров`,
        description: `Итоговый балл: ${ac.total_score}. Подробные характеристики и видеообзор.`,
      },
    };
  } catch {
    return { title: "Кондиционер не найден" };
  }
}

export default async function ConditionerPage({ params }: Props) {
  const { id } = await params;
  let ac;
  try {
    ac = await getConditioner(Number(id));
  } catch {
    notFound();
  }

  const maxScore = Math.max(...ac.parameters.map((p) => p.score), 1);

  return (
    <article>
      <BackLink href="/" />

      <header className="mb-8">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
              {ac.brand}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {ac.model_name}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Итоговый балл
            </div>
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {ac.total_score.toFixed(1)}
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <section aria-label="Параметры кондиционера">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Параметры
          </h2>
          <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-4">
            {ac.parameters.map((param) => (
              <ParameterBar
                key={param.id}
                parameter={param}
                maxScore={maxScore}
              />
            ))}
          </div>
        </section>

        <aside>
          <VideoLinks
            youtube_url={ac.youtube_url}
            rutube_url={ac.rutube_url}
            vk_url={ac.vk_url}
          />
        </aside>
      </div>
    </article>
  );
}
