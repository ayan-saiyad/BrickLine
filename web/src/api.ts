import type { Filters, ImportStatus, SetPage } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "/api";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new Error(`request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function getSets(filters: Filters): Promise<SetPage> {
  const params = new URLSearchParams({ page_size: "250" });
  if (filters.query.trim()) params.set("q", filters.query.trim());
  filters.themes.forEach((theme) => params.append("theme", theme));
  filters.statuses.forEach((status) => params.append("status", status));
  return request<SetPage>(`/sets?${params}`);
}

export function getThemes(): Promise<string[]> {
  return request<string[]>("/themes");
}

export function getImportStatus(): Promise<ImportStatus> {
  return request<ImportStatus>("/imports/status");
}

