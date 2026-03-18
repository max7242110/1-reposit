import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

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
    <div>
      <Link
        href="/"
        className="inline-flex items-center gap-1 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 mb-6 transition-colors"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        Назад к рейтингу
      </Link>

      <div className="mb-8">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
              {ac.brand}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {ac.model_name}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Итоговый балл
              </div>
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {ac.total_score.toFixed(1)}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
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
        </div>

        <div>
          <VideoLinks
            youtube_url={ac.youtube_url}
            rutube_url={ac.rutube_url}
            vk_url={ac.vk_url}
          />
        </div>
      </div>
    </div>
  );
}
