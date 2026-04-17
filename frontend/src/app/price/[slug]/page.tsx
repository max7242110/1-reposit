import type { Metadata } from "next";
import { notFound } from "next/navigation";
import RatingPageContent from "@/components/RatingPageContent";
import { getMethodology, getModels } from "@/lib/api";
import { getRatingYear } from "@/lib/year";

interface PriceTier {
  slug: string;
  max: number;
}

export const PRICE_TIERS: readonly PriceTier[] = [
  { slug: "do-20000-rub", max: 20000 },
  { slug: "do-25000-rub", max: 25000 },
  { slug: "do-30000-rub", max: 30000 },
  { slug: "do-35000-rub", max: 35000 },
  { slug: "do-40000-rub", max: 40000 },
  { slug: "do-50000-rub", max: 50000 },
  { slug: "do-60000-rub", max: 60000 },
] as const;

const formatRub = (n: number) =>
  new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(n);

interface Props {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export const revalidate = 86400;

export function generateStaticParams() {
  return PRICE_TIERS.map((t) => ({ slug: t.slug }));
}

function getTier(slug: string): PriceTier | undefined {
  return PRICE_TIERS.find((t) => t.slug === slug);
}

export async function generateMetadata({ params, searchParams }: Props): Promise<Metadata> {
  const { slug } = await params;
  const tier = getTier(slug);
  if (!tier) return { title: "Страница не найдена" };

  const sp = await searchParams;
  const hasFilters = Object.keys(sp).length > 0;
  const year = getRatingYear();
  const canonical = `/price/${tier.slug}`;

  return {
    title: `Кондиционеры до ${formatRub(tier.max)} ₽ — рейтинг ${year}`,
    description: `Рейтинг бытовых кондиционеров и сплит-систем с ценой до ${formatRub(tier.max)} ₽. Независимые измерения шума, вибрации и качества комплектующих.`,
    alternates: { canonical },
    robots: hasFilters
      ? { index: false, follow: true }
      : { index: true, follow: true },
    openGraph: {
      title: `Кондиционеры до ${formatRub(tier.max)} ₽ — рейтинг ${year}`,
      description: `Независимый рейтинг кондиционеров в ценовом диапазоне до ${formatRub(tier.max)} ₽.`,
      url: canonical,
    },
  };
}

export default async function PriceTierPage({ params }: Props) {
  const { slug } = await params;
  const tier = getTier(slug);
  if (!tier) notFound();

  const year = getRatingYear();

  const [models, methodology] = await Promise.all([
    getModels({ price_max: String(tier.max) }),
    getMethodology().catch(() => null),
  ]);

  return (
    <RatingPageContent
      models={models}
      methodology={methodology}
      heading={`Рейтинг кондиционеров до ${formatRub(tier.max)} ₽`}
      intro={`Независимый рейтинг ${year} года: бытовые кондиционеры и сплит-системы с ценой до ${formatRub(tier.max)} ₽ на основе реальных измерений.`}
      seoBlock={
        <div className="mt-10 p-6 bg-gray-50 dark:bg-gray-900 rounded-xl">
          <div className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Как выбрать кондиционер до {formatRub(tier.max)} ₽
            </h2>
            <p>
              В ценовом сегменте до {formatRub(tier.max)} ₽ представлены бытовые
              кондиционеры и сплит-системы, которые прошли независимое тестирование
              в лаборатории «Август-климат». Каждая модель оценивается по множеству
              параметров: уровень шума, вибрация наружного блока, качество
              комплектующих, площадь теплообменников и функциональность.
            </p>
            <p>
              Рейтинг поможет выбрать оптимальную сплит-систему в рамках вашего
              бюджета. Мы не опираемся на каталожные данные производителей —
              все показатели получены в результате реальных замеров. Это позволяет
              объективно сравнить кондиционеры разных брендов между собой и найти
              лучшее соотношение цены и качества.
            </p>
            <p>
              Если вашей модели нет в рейтинге, вы можете{" "}
              <a href="/submit" className="text-blue-600 dark:text-blue-400 hover:underline">
                подать заявку
              </a>{" "}
              на тестирование, и мы включим её после проведения измерений.
            </p>
          </div>
        </div>
      }
    />
  );
}
