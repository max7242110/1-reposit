export default function DetailSkeleton() {
  return (
    <div className="animate-pulse" aria-busy="true" aria-label="Загрузка данных">
      <div className="h-4 w-32 bg-gray-200 dark:bg-gray-800 rounded mb-6" />
      <div className="flex items-start justify-between mb-8">
        <div>
          <div className="h-8 w-64 bg-gray-200 dark:bg-gray-800 rounded mb-2" />
          <div className="h-4 w-96 bg-gray-200 dark:bg-gray-800 rounded" />
        </div>
        <div className="h-12 w-24 bg-gray-200 dark:bg-gray-800 rounded" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-12 bg-gray-200 dark:bg-gray-800 rounded" />
          ))}
        </div>
        <div className="h-64 bg-gray-200 dark:bg-gray-800 rounded" />
      </div>
    </div>
  );
}
