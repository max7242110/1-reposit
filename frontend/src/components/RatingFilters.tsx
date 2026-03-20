"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useRef } from "react";

const DEBOUNCE_MS = 400;

export default function RatingFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const updateParam = useCallback(
    (key: string, value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
      const basePath = window.location.pathname.startsWith("/v2") ? "/v2" : "/";
      router.push(`${basePath}?${params.toString()}`);
    },
    [router, searchParams],
  );

  const handleBrandChange = useCallback(
    (value: string) => {
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => updateParam("brand", value), DEBOUNCE_MS);
    },
    [updateParam],
  );

  return (
    <div className="flex flex-wrap gap-3 mb-6" role="search" aria-label="Фильтры рейтинга">
      <label className="sr-only" htmlFor="brand-filter">Поиск по бренду</label>
      <input
        id="brand-filter"
        type="text"
        placeholder="Поиск по бренду..."
        defaultValue={searchParams.get("brand") || ""}
        onChange={(e) => handleBrandChange(e.target.value)}
        aria-label="Поиск по бренду"
        className="px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
      />
      <label className="sr-only" htmlFor="region-filter">Выберите регион</label>
      <select
        id="region-filter"
        defaultValue={searchParams.get("region") || ""}
        onChange={(e) => updateParam("region", e.target.value)}
        aria-label="Фильтр по региону"
        className="px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
      >
        <option value="">Все регионы</option>
        <option value="ru">Россия</option>
        <option value="eu">Европа</option>
      </select>
    </div>
  );
}
