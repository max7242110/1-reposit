import { AirConditionerDetail, AirConditionerSummary } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function getConditioners(): Promise<AirConditionerSummary[]> {
  const res = await fetch(`${API_BASE}/conditioners/`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getConditioner(id: number): Promise<AirConditionerDetail> {
  const res = await fetch(`${API_BASE}/conditioners/${id}/`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
