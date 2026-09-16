export type EventType = "release" | "retirement";
export type Confidence = "confirmed" | "estimated";
export type SetStatus = "upcoming" | "available" | "retiring" | "retired";

export interface ReleaseEvent {
  event_type: EventType;
  event_date: string;
  confidence: Confidence;
  source_name: string;
  source_url: string;
}

export interface LegoSet {
  set_number: string;
  name: string;
  theme: string;
  piece_count: number | null;
  image_url: string | null;
  status: SetStatus;
  events: ReleaseEvent[];
}

export interface SetPage {
  items: LegoSet[];
  total: number;
  page: number;
  page_size: number;
}

export interface ImportRun {
  id: number;
  source_name: string;
  state: "running" | "succeeded" | "failed";
  started_at: string;
  finished_at: string | null;
  imported_count: number;
  rejected_count: number;
  error: string | null;
}

export interface ImportStatus {
  latest_run: ImportRun | null;
  latest_success: ImportRun | null;
  data_age_seconds: number | null;
}

export interface Filters {
  query: string;
  themes: string[];
  statuses: SetStatus[];
  watchlistOnly: boolean;
}

export interface CalendarItem {
  set: LegoSet;
  event: ReleaseEvent;
  date: Date;
}

