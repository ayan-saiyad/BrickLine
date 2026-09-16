import { describe, expect, it } from "vitest";
import { eventsForSets, formatDataAge, monthCells } from "../lib";
import type { LegoSet } from "../types";

describe("calendar helpers", () => {
  it("builds complete calendar weeks", () => {
    const cells = monthCells(new Date(2026, 8, 1));
    expect(cells).toHaveLength(35);
    expect(cells.filter(Boolean)).toHaveLength(30);
  });

  it("sorts events by date", () => {
    const sets: LegoSet[] = [
      {
        set_number: "1",
        name: "Test",
        theme: "Ideas",
        piece_count: null,
        image_url: null,
        status: "upcoming",
        events: [
          {
            event_type: "retirement",
            event_date: "2027-01-01",
            confidence: "estimated",
            source_name: "Example",
            source_url: "https://example.com",
          },
          {
            event_type: "release",
            event_date: "2026-01-01",
            confidence: "confirmed",
            source_name: "Example",
            source_url: "https://example.com",
          },
        ],
      },
    ];

    expect(eventsForSets(sets)[0].event.event_type).toBe("release");
  });

  it("formats freshness in useful units", () => {
    expect(formatDataAge(300)).toBe("Updated less than an hour ago");
    expect(formatDataAge(7200)).toBe("Updated 2 hours ago");
    expect(formatDataAge(172800)).toBe("Updated 2 days ago");
  });
});

