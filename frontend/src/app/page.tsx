import RatingTable from "@/components/RatingTable";
import { getConditioners } from "@/lib/api";

export default async function HomePage() {
  const conditioners = await getConditioners();

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Рейтинг бытовых кондиционеров
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Независимый рейтинг на основе реальных измерений. Чем выше суммарный
          индекс — тем лучше кондиционер по совокупности параметров.
        </p>
      </div>
      <RatingTable conditioners={conditioners} />
    </div>
  );
}
