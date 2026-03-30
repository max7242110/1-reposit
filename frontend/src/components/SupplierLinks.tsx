import { Supplier } from "@/lib/types";

interface Props {
  suppliers: Supplier[];
}

export default function SupplierLinks({ suppliers }: Props) {
  if (suppliers.length === 0) return null;

  return (
    <section aria-label="Где купить">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">Где купить</h2>
      <div className="space-y-2">
        {suppliers.map((s) => (
          <a
            key={s.id}
            href={s.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors text-sm font-medium text-blue-600 dark:text-blue-400"
          >
            <span className="flex-1">{s.name}</span>
            <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        ))}
      </div>
    </section>
  );
}
