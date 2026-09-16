import type { CalendarItem, LegoSet } from "./types";

export function parseDate(value: string): Date {
  return new Date(`${value}T12:00:00`);
}

export function eventsForSets(sets: LegoSet[]): CalendarItem[] {
  return sets
    .flatMap((set) =>
      set.events.map((event) => ({ set, event, date: parseDate(event.event_date) })),
    )
    .sort((a, b) => a.date.getTime() - b.date.getTime());
}

export function monthCells(month: Date): Array<Date | null> {
  const year = month.getFullYear();
  const monthIndex = month.getMonth();
  const firstDay = new Date(year, monthIndex, 1).getDay();
  const days = new Date(year, monthIndex + 1, 0).getDate();
  const cells: Array<Date | null> = Array.from({ length: firstDay }, () => null);
  for (let day = 1; day <= days; day += 1) cells.push(new Date(year, monthIndex, day));
  while (cells.length % 7) cells.push(null);
  return cells;
}

export function sameDay(left: Date, right: Date): boolean {
  return (
    left.getFullYear() === right.getFullYear() &&
    left.getMonth() === right.getMonth() &&
    left.getDate() === right.getDate()
  );
}

export function formatDate(date: Date, options?: Intl.DateTimeFormatOptions): string {
  return new Intl.DateTimeFormat("en-US", options ?? { month: "short", day: "numeric" }).format(
    date,
  );
}

export function formatDataAge(seconds: number | null): string {
  if (seconds === null) return "No successful import yet";
  const hours = Math.max(0, Math.floor(seconds / 3600));
  if (hours < 1) return "Updated less than an hour ago";
  if (hours < 24) return `Updated ${hours} ${hours === 1 ? "hour" : "hours"} ago`;
  const days = Math.floor(hours / 24);
  return `Updated ${days} ${days === 1 ? "day" : "days"} ago`;
}

export function loadWatchlist(): Set<string> {
  try {
    const stored = JSON.parse(localStorage.getItem("brickline-watchlist") || "[]") as unknown;
    return new Set(Array.isArray(stored) ? stored.filter((item) => typeof item === "string") : []);
  } catch {
    return new Set();
  }
}

