interface Props {
  prosText: string;
  consText: string;
}

function renderLines(text: string): string[] {
  return text
    .split("\n")
    .map((line) => line.replace(/^[-•✓✗]\s*/, "").trim())
    .filter(Boolean);
}

export default function ProsConsBlock({ prosText, consText }: Props) {
  if (!prosText && !consText) return null;

  return (
    <section aria-label="Плюсы и минусы">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Плюсы и минусы</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {prosText && (
          <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-green-700 dark:text-green-400 mb-2">Плюсы</h3>
            <ul className="space-y-1.5">
              {renderLines(prosText).map((line, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-green-800 dark:text-green-300">
                  <span className="mt-0.5 shrink-0 text-green-600">✓</span>
                  <span>{line}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {consText && (
          <div className="bg-red-50 dark:bg-red-900/20 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-red-700 dark:text-red-400 mb-2">Минусы</h3>
            <ul className="space-y-1.5">
              {renderLines(consText).map((line, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-red-800 dark:text-red-300">
                  <span className="mt-0.5 shrink-0 text-red-500">✗</span>
                  <span>{line}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
