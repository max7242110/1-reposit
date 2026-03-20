"use client";

interface Props {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorPage({ error, reset }: Props) {
  return (
    <div className="flex items-center justify-center min-h-[40vh]">
      <div className="text-center max-w-md">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Что-то пошло не так
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Не удалось загрузить данные. Проверьте подключение к интернету и попробуйте снова.
        </p>
        <button
          onClick={reset}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Попробовать снова
        </button>
      </div>
    </div>
  );
}
