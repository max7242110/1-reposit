"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useRef } from "react";

const DEBOUNCE_MS = 400;

interface Props {
  defaultPriceMin?: number;
  defaultPriceMax?: number;
}

export default function RatingFilters({ defaultPriceMin, defaultPriceMax }: Props) {
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

  const handleDebounced = useCallback(
    (key: string, value: string) => {
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => updateParam(key, value), DEBOUNCE_MS);
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
        onChange={(e) => handleDebounced("brand", e.target.value)}
        aria-label="Поиск по бренду"
        className="px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
      />
      <label className="sr-only" htmlFor="price-min-filter">Цена от</label>
      <input
        id="price-min-filter"
        type="number"
        placeholder={defaultPriceMin ? `от ${defaultPriceMin.toLocaleString("ru-RU")} ₽` : "Цена от (₽)"}
        defaultValue={searchParams.get("price_min") || ""}
        onChange={(e) => handleDebounced("price_min", e.target.value)}
        aria-label="Цена от"
        min={0}
        className="px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none w-36"
      />
      <label className="sr-only" htmlFor="price-max-filter">Цена до</label>
      <input
        id="price-max-filter"
        type="number"
        placeholder={defaultPriceMax ? `до ${defaultPriceMax.toLocaleString("ru-RU")} ₽` : "Цена до (₽)"}
        defaultValue={searchParams.get("price_max") || ""}
        onChange={(e) => handleDebounced("price_max", e.target.value)}
        aria-label="Цена до"
        min={0}
        className="px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none w-36"
      />
    </div>
  );
}
