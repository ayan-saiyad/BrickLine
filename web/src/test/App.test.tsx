import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../App";

const responses: Record<string, unknown> = {
  "/api/themes": ["Ideas"],
  "/api/imports/status": {
    latest_run: null,
    latest_success: null,
    data_age_seconds: null,
  },
};

describe("App", () => {
  afterEach(() => vi.restoreAllMocks());

  it("loads sets into the calendar", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: string | URL | Request) => {
        const url = String(input);
        const body = url.includes("/api/sets")
          ? {
              items: [
                {
                  set_number: "100-1",
                  name: "Little House",
                  theme: "Ideas",
                  piece_count: 100,
                  image_url: null,
                  status: "available",
                  events: [],
                },
              ],
              total: 1,
              page: 1,
              page_size: 250,
            }
          : responses[new URL(url, "http://local").pathname];
        return Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));
      }),
    );

    render(<App />);

    await waitFor(() => expect(screen.getByTestId("results-summary")).toHaveTextContent("1 set"));
    expect(screen.getByPlaceholderText(/search by set/i)).toBeInTheDocument();
  });
});
