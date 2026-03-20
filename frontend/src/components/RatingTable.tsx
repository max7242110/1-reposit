import Link from "next/link";
import { AirConditionerSummary } from "@/lib/types";
import { getMedalColor } from "@/lib/utils";

interface Props {
  conditioners: AirConditionerSummary[];
}

export default function RatingTable({ conditioners }: Props) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse" role="table">
        <caption className="sr-only">
          Рейтинг бытовых кондиционеров по суммарному индексу
        </caption>
        <thead>
          <tr className="border-b-2 border-gray-200 dark:border-gray-700">
            <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300 w-16">
              #
            </th>
            <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300">
              Бренд
            </th>
            <th scope="col" className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300 hidden sm:table-cell">
              Модель
            </th>
            <th scope="col" className="px-4 py-3 text-right text-sm font-semibold text-gray-600 dark:text-gray-300 w-28">
              Баллы
            </th>
          </tr>
        </thead>
        <tbody>
          {conditioners.map((ac, idx) => (
            <tr
              key={ac.id}
              className="border-b border-gray-100 dark:border-gray-800 hover:bg-blue-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <td className="px-4 py-4">
                <span className={`text-lg font-bold ${getMedalColor(idx + 1)}`}>
                  {idx + 1}
                </span>
              </td>
              <td className="px-4 py-4">
                <Link
                  href={`/conditioner/${ac.id}`}
                  className="font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  {ac.brand}
                </Link>
                <div className="text-sm text-gray-500 dark:text-gray-400 sm:hidden mt-0.5">
                  {ac.model_name}
                </div>
              </td>
              <td className="px-4 py-4 text-sm text-gray-600 dark:text-gray-400 hidden sm:table-cell">
                {ac.model_name}
              </td>
              <td className="px-4 py-4 text-right">
                <span className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 font-semibold text-sm">
                  {ac.total_score.toFixed(1)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
