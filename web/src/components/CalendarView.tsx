import { useMemo } from "react";
import { formatDate, monthCells, sameDay } from "../lib";
import type { CalendarItem, LegoSet } from "../types";

interface Props {
  items: CalendarItem[];
  month: Date;
  onMonthChange: (month: Date) => void;
  onSelect: (set: LegoSet) => void;
  onNextEvent: () => void;
}

const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function CalendarView({ items, month, onMonthChange, onSelect, onNextEvent }: Props) {
  const cells = useMemo(() => monthCells(month), [month]);
  const title = formatDate(month, { month: "long", year: "numeric" });

  const shiftMonth = (amount: number) => {
    onMonthChange(new Date(month.getFullYear(), month.getMonth() + amount, 1));
  };

  return (
    <section className="calendar-card" aria-label={`${title} release calendar`}>
      <div className="calendar-toolbar">
        <div>
          <span className="eyebrow">Release calendar</span>
          <h2>{title}</h2>
        </div>
        <div className="calendar-actions">
          <button className="quiet-button" onClick={onNextEvent}>
            Next event
          </button>
          <div className="month-nav">
            <button onClick={() => shiftMonth(-1)} aria-label="Previous month">
              ←
            </button>
            <button onClick={() => onMonthChange(new Date())}>Today</button>
            <button onClick={() => shiftMonth(1)} aria-label="Next month">
              →
            </button>
          </div>
        </div>
      </div>

      <div className="calendar-grid weekdays" aria-hidden="true">
        {weekdays.map((day) => (
          <div key={day}>{day}</div>
        ))}
      </div>
      <div className="calendar-grid month-days">
        {cells.map((day, index) => {
          if (!day) return <div className="day empty" key={`empty-${index}`} />;
          const dayItems = items.filter((item) => sameDay(item.date, day));
          return (
            <div className={`day ${sameDay(day, new Date()) ? "today" : ""}`} key={day.toISOString()}>
              <span className="day-number">{day.getDate()}</span>
              <div className="day-events">
                {dayItems.slice(0, 3).map((item) => (
                  <button
                    className={`calendar-event ${item.event.event_type}`}
                    key={`${item.set.set_number}-${item.event.event_type}`}
                    onClick={() => onSelect(item.set)}
                    title={`${item.set.name} — ${item.event.event_type}`}
                  >
                    <span>{item.set.name}</span>
                    {item.event.confidence === "estimated" && <i>est.</i>}
                  </button>
                ))}
                {dayItems.length > 3 && <span className="more-events">+{dayItems.length - 3} more</span>}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

