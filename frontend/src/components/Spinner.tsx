interface Props {
  text?: string;
}

export default function Spinner({ text = "Загрузка рейтинга..." }: Props) {
  return (
    <div className="flex items-center justify-center min-h-[40vh]">
      <div className="text-center" role="status" aria-live="polite">
        <div
          className="inline-block w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"
          aria-hidden="true"
        />
        <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">{text}</p>
      </div>
    </div>
  );
}
