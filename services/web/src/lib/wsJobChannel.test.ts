import { describe, expect, it, vi } from "vitest";

import { jobChannelWsUrl } from "./wsJobChannel";

vi.mock("./env", () => ({
  getApiBase: (): string => "http://localhost:8010",
}));

describe("jobChannelWsUrl", () => {
  it("usa ws:// e query client_session", () => {
    const jid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee";
    const cs = "11111111-2222-4333-8444-555555555555";
    expect(jobChannelWsUrl(jid, cs)).toBe(
      `ws://localhost:8010/ws/jobs/${encodeURIComponent(jid)}?client_session=${encodeURIComponent(cs)}`,
    );
  });
});
