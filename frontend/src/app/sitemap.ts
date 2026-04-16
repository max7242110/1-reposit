import type { MetadataRoute } from "next";
import { PRICE_TIERS } from "@/app/price/[slug]/page";
import { getModels } from "@/lib/api";

export const revalidate = 86400;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
  const now = new Date();

  const staticEntries: MetadataRoute.Sitemap = [
    {
      url: `${baseUrl}/`,
      lastModified: now,
      changeFrequency: "daily",
      priority: 1.0,
    },
    {
      url: `${baseUrl}/methodology`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.6,
    },
    {
      url: `${baseUrl}/quiet`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.8,
    },
    ...PRICE_TIERS.map((t) => ({
      url: `${baseUrl}/price/${t.slug}`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.8,
    })),
  ];

  let modelEntries: MetadataRoute.Sitemap = [];
  try {
    const models = await getModels();
    modelEntries = models.map((m) => ({
      url: `${baseUrl}/${m.slug}`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.7,
    }));
  } catch {
    modelEntries = [];
  }

  return [...staticEntries, ...modelEntries];
}
