import type { Dispatch, SetStateAction } from "react";
import type { Filters, SetStatus } from "../types";

const statuses: Array<{ value: SetStatus; label: string }> = [
  { value: "upcoming", label: "Upcoming" },
  { value: "available", label: "Available" },
  { value: "retiring", label: "Retiring soon" },
  { value: "retired", label: "Retired" },
];

interface Props {
  filters: Filters;
  setFilters: Dispatch<SetStateAction<Filters>>;
  themes: string[];
  watchlistSize: number;
}

export function FiltersPanel({ filters, setFilters, themes, watchlistSize }: Props) {
  const toggleTheme = (theme: string) => {
    setFilters((current) => ({
      ...current,
      themes: current.themes.includes(theme)
        ? current.themes.filter((item) => item !== theme)
        : [...current.themes, theme],
    }));
  };

  const toggleStatus = (status: SetStatus) => {
    setFilters((current) => ({
      ...current,
      statuses: current.statuses.includes(status)
        ? current.statuses.filter((item) => item !== status)
        : [...current.statuses, status],
    }));
  };

  return (
    <aside className="filters" aria-label="Filters">
      <div className="filter-heading">
        <h2>Filters</h2>
        {(filters.themes.length > 0 || filters.statuses.length > 0) && (
          <button
            className="text-button"
            onClick={() => setFilters((current) => ({ ...current, themes: [], statuses: [] }))}
          >
            Clear
          </button>
        )}
      </div>

      <fieldset>
        <legend>Status</legend>
        {statuses.map((status) => (
          <label className="check-row" key={status.value}>
            <input
              type="checkbox"
              checked={filters.statuses.includes(status.value)}
              onChange={() => toggleStatus(status.value)}
            />
            <span>{status.label}</span>
          </label>
        ))}
      </fieldset>

      <fieldset>
        <legend>Theme</legend>
        <div className="theme-list">
          {themes.map((theme) => (
            <label className="check-row" key={theme}>
              <input
                type="checkbox"
                checked={filters.themes.includes(theme)}
                onChange={() => toggleTheme(theme)}
              />
              <span>{theme}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <button
        className={`watch-filter ${filters.watchlistOnly ? "active" : ""}`}
        onClick={() =>
          setFilters((current) => ({ ...current, watchlistOnly: !current.watchlistOnly }))
        }
      >
        <span aria-hidden="true">★</span>
        My watchlist
        <b>{watchlistSize}</b>
      </button>
    </aside>
  );
}

