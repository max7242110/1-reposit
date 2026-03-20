export function getMedalColor(position: number): string {
  if (position === 1) return "text-yellow-500";
  if (position === 2) return "text-gray-400";
  if (position === 3) return "text-amber-700";
  return "text-gray-500";
}
