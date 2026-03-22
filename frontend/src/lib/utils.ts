/** Формат правой части «индекс / максимум» (целые без .0). */
export function formatIndexMax(n: number): string {
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}

export function getMedalColor(position: number): string {
  if (position === 1) return "text-yellow-500";
  if (position === 2) return "text-gray-400";
  if (position === 3) return "text-amber-700";
  return "text-gray-500";
}
