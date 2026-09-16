import { useCallback, useEffect, useMemo, useState } from "react";
import { getImportStatus, getSets, getThemes } from "./api";
import { Brand } from "./components/Brand";
import { CalendarView } from "./components/CalendarView";
import { FiltersPanel } from "./components/FiltersPanel";
import { SetDrawer } from "./components/SetDrawer";
import { TimelineView } from "./components/TimelineView";
import { eventsForSets, formatDataAge, loadWatchlist } from "./lib";
import type { Filters, ImportStatus, LegoSet } from "./types";
import "./styles.css";

const initialFilters: Filters = {
  query: "",
  themes: [],
  statuses: [],
  watchlistOnly: false,
};

export default function App() {
  const [filters, setFilters] = useState(initialFilters);
  const [sets, setSets] = useState<LegoSet[]>([]);
  const [themes, setThemes] = useState<string[]>([]);
  const [status, setStatus] = useState<ImportStatus | null>(null);
  const [watchlist, setWatchlist] = useState(loadWatchlist);
  const [view, setView] = useState<"calendar" | "timeline">("calendar");
  const [month, setMonth] = useState(() => new Date());
  const [selected, setSelected] = useState<LegoSet | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getThemes().then(setThemes).catch(() => undefined);
    getImportStatus().then(setStatus).catch(() => undefined);
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setLoading(true);
      getSets(filters)
        .then((page) => {
          setSets(page.items);
          setError("");
        })
        .catch(() => setError("Could not reach the calendar service."))
        .finally(() => setLoading(false));
    }, 180);
    return () => window.clearTimeout(timer);
  }, [filters.query, filters.themes, filters.statuses]);

  const visibleSets = useMemo(
    () => (filters.watchlistOnly ? sets.filter((set) => watchlist.has(set.set_number)) : sets),
    [filters.watchlistOnly, sets, watchlist],
  );
  const events = useMemo(() => eventsForSets(visibleSets), [visibleSets]);

  const toggleWatch = useCallback((setNumber: string) => {
    setWatchlist((current) => {
      const next = new Set(current);
      if (next.has(setNumber)) next.delete(setNumber);
      else next.add(setNumber);
      localStorage.setItem("brickline-watchlist", JSON.stringify([...next]));
      return next;
    });
  }, []);

  const jumpToNextEvent = () => {
    const now = new Date();
    const next = events.find((item) => item.date >= now) ?? events[0];
    if (next) setMonth(new Date(next.date.getFullYear(), next.date.getMonth(), 1));
  };

  return (
    <div className="app-shell">
      <header className="site-header">
        <Brand />
        <nav aria-label="Primary navigation">
          <a className="active" href="#calendar">
            Calendar
          </a>
          <a href="#about">About</a>
        </nav>
        <div className="freshness" title="Age of the latest successful data import">
          <i className={status?.latest_run?.state === "failed" ? "warning" : ""} />
          {formatDataAge(status?.data_age_seconds ?? null)}
        </div>
      </header>

      <main id="calendar">
        <section className="hero">
          <div>
            <span className="eyebrow">LEGO release tracker</span>
            <h1>Plan the next build.</h1>
            <p>Release dates, retirement estimates, and the sets worth keeping an eye on.</p>
          </div>
          <label className="search-box">
            <span aria-hidden="true">⌕</span>
            <input
              type="search"
              placeholder="Search by set name or number"
              value={filters.query}
              onChange={(event) =>
                setFilters((current) => ({ ...current, query: event.target.value }))
              }
            />
          </label>
        </section>

        <div className="workspace">
          <FiltersPanel
            filters={filters}
            setFilters={setFilters}
            themes={themes}
            watchlistSize={watchlist.size}
          />

          <section className="results">
            <div className="results-bar">
              <span data-testid="results-summary">
                <b>{events.length}</b> dated events from <b>{visibleSets.length}</b>{" "}
                {visibleSets.length === 1 ? "set" : "sets"}
              </span>
              <div className="view-toggle" aria-label="Choose view">
                <button
                  className={view === "calendar" ? "active" : ""}
                  onClick={() => setView("calendar")}
                >
                  Calendar
                </button>
                <button
                  className={view === "timeline" ? "active" : ""}
                  onClick={() => setView("timeline")}
                >
                  Timeline
                </button>
              </div>
            </div>

            {error && <div className="error-banner">{error} Try again in a moment.</div>}
            {loading ? (
              <div className="loading-grid" aria-label="Loading calendar">
                {Array.from({ length: 12 }, (_, index) => (
                  <i key={index} />
                ))}
              </div>
            ) : view === "calendar" ? (
              <CalendarView
                items={events}
                month={month}
                onMonthChange={setMonth}
                onSelect={setSelected}
                onNextEvent={jumpToNextEvent}
              />
            ) : (
              <TimelineView items={events} onSelect={setSelected} />
            )}
          </section>
        </div>
      </main>

      <footer id="about">
        <Brand />
        <p>Dates stay attached to their sources. Estimates stay labeled.</p>
        <span>Built for collectors who like a plan.</span>
      </footer>

      {selected && (
        <SetDrawer
          legoSet={selected}
          watched={watchlist.has(selected.set_number)}
          onClose={() => setSelected(null)}
          onToggleWatch={toggleWatch}
        />
      )}
    </div>
  );
}
