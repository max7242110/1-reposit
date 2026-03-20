import { RegionAvailability } from "@/lib/types";

interface Props {
  regions: RegionAvailability[];
}

const FLAG: Record<string, string> = {
  ru: "RU",
  eu: "EU",
};

export default function RegionBadges({ regions }: Props) {
  if (!regions.length) return null;
  return (
    <div className="flex gap-1">
      {regions.map((r) => (
        <span
          key={r.region_code}
          className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
        >
          {FLAG[r.region_code] || r.region_display}
        </span>
      ))}
    </div>
  );
}
