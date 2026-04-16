import type { Metadata } from "next";
import RatingPageContent from "@/components/RatingPageContent";
import { getMethodology, getModels } from "@/lib/api";
import { getRatingYear } from "@/lib/year";

interface Props {
  searchParams: Promise<{ brand?: string; price_min?: string; price_max?: string }>;
}

export const revalidate = 86400;

export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
  const params = await searchParams;
  const hasFilters = Object.keys(params).length > 0;
  const year = getRatingYear();

  return {
    title: `Рейтинг кондиционеров ${year}`,
    description: `Независимый рейтинг бытовых кондиционеров ${year}: шум, вибрация, качество комплектующих, функциональность. Реальные измерения.`,
    alternates: { canonical: "/" },
    robots: hasFilters
      ? { index: false, follow: true }
      : { index: true, follow: true },
  };
}

export default async function HomePage({ searchParams }: Props) {
  const params = await searchParams;
  const filters: Record<string, string> = {};
  if (params.brand) filters.brand = params.brand;
  if (params.price_min) filters.price_min = params.price_min;
  if (params.price_max) filters.price_max = params.price_max;

  const [models, methodology] = await Promise.all([
    getModels(Object.keys(filters).length ? filters : undefined),
    getMethodology().catch(() => null),
  ]);

  return <RatingPageContent models={models} methodology={methodology} />;
}
