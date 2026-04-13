import Link from "next/link";
import { ACModelSummary } from "@/lib/types";
import { formatIndexMax, getMedalColor } from "@/lib/utils";

interface Props {
  models: ACModelSummary[];
  /** standard — total_index, noise — noise_score */
  indexMode?: "standard" | "noise";
  /** Пользовательский рейтинг: {model_id: custom_score} */
  customIndex?: Record<number, number>;
}

function formatPrice(price: string | null): string {
  if (!price) return "—";
  const num = parseFloat(price);
  if (isNaN(num)) return "—";
  return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(num) + " ₽";
}

export default function RatingTableV2({ models, indexMode = "standard", customIndex }: Props) {
  const indexLabel = customIndex
    ? "Свой индекс"
    : indexMode === "noise"
      ? "Шум (балл)"
      : "Индекс";

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse" role="table">
        <caption className="sr-only">
          Рейтинг бытовых кондиционеров по индексу «Август-климат»
        </caption>
        <thead>
          <tr className="border-b-2 border-gray-200 dark:border-gray-700">
            <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300 w-12">#</th>
            <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300">Бренд</th>
            <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300 hidden sm:table-cell">Модель</th>
            <th scope="col" className="px-4 py-3 text-right text-sm font-semibold text-gray-600 dark:text-gray-300 hidden md:table-cell">Цена</th>
            <th scope="col" className="px-4 py-3 text-right text-sm font-semibold text-gray-600 dark:text-gray-300 min-w-[7.5rem]">{indexLabel}</th>
          </tr>
        </thead>
        <tbody>
          {models.map((m, idx) => {
            let indexDisplay: React.ReactNode;
            if (customIndex) {
              const score = customIndex[m.id] ?? 0;
              indexDisplay = (
                <span className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-purple-100 dark:bg-purple-900/40 text-purple-800 dark:text-purple-300 font-semibold text-sm tabular-nums whitespace-nowrap">
                  {score.toFixed(1)}
                </span>
              );
            } else if (indexMode === "noise") {
              const score = m.noise_score ?? 0;
              indexDisplay = (
                <span className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 font-semibold text-sm tabular-nums whitespace-nowrap">
                  {score.toFixed(1)}
                </span>
              );
            } else {
              indexDisplay = (
                <span className="inline-flex items-center justify-center gap-1 px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 font-semibold text-sm tabular-nums whitespace-nowrap">
                  <span>{m.total_index.toFixed(1)}</span>
                  <span className="font-normal text-blue-600/80 dark:text-blue-400/80">/</span>
                  <span>{formatIndexMax(m.index_max ?? 100)}</span>
                </span>
              );
            }

            return (
              <tr
                key={m.id}
                className="border-b border-gray-100 dark:border-gray-800 hover:bg-blue-50 dark:hover:bg-gray-800/50 transition-colors"
              >
                <td className="px-4 py-4">
                  <span className={`text-lg font-bold ${getMedalColor(idx + 1)}`}>{idx + 1}</span>
                </td>
                <td className="px-4 py-4">
                  <Link
                    href={`/${m.slug}`}
                    className="inline-flex items-center gap-2 font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                  >
                    {m.brand_logo && (
                      <img
                        src={m.brand_logo}
                        alt=""
                        className="h-5 w-5 object-contain shrink-0"
                        loading="lazy"
                      />
                    )}
                    {m.brand}
                  </Link>
                  <div className="text-sm text-gray-500 dark:text-gray-400 sm:hidden mt-0.5">
                    {m.inner_unit}
                  </div>
                </td>
                <td className="px-4 py-4 text-sm text-gray-600 dark:text-gray-400 hidden sm:table-cell">
                  {m.inner_unit}
                </td>
                <td className="px-4 py-4 text-right text-sm text-gray-600 dark:text-gray-400 hidden md:table-cell tabular-nums">
                  {formatPrice(m.price)}
                </td>
                <td className="px-4 py-4 text-right">
                  {indexDisplay}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
