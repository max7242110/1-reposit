import RatingPageContent from "@/components/RatingPageContent";
import { getMethodology, getModels } from "@/lib/api";

interface Props {
  searchParams: Promise<{ brand?: string; price_min?: string; price_max?: string }>;
}

export default async function RatingPageV2({ searchParams }: Props) {
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
