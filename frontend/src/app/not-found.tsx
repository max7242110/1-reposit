import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-[40vh]">
      <div className="text-center">
        <h2 className="text-6xl font-bold text-gray-200 dark:text-gray-800 mb-4">
          404
        </h2>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Страница не найдена
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Возможно, кондиционер был удалён из рейтинга.
        </p>
        <Link
          href="/"
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Вернуться к рейтингу
        </Link>
      </div>
    </div>
  );
}
