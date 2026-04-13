/** Формат правой части «индекс / максимум» (целые без .0). */
export function formatIndexMax(n: number): string {
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}

/** Склонение числительных для лет: 1 год, 2 года, 5 лет. */
export function formatYears(raw: string): string {
  const n = parseInt(raw, 10);
  if (isNaN(n)) return raw;
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return `${n} год`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return `${n} года`;
  return `${n} лет`;
}

export function getMedalColor(position: number): string {
  if (position === 1) return "text-yellow-500";
  if (position === 2) return "text-gray-400";
  if (position === 3) return "text-amber-700";
  return "text-gray-500";
}
