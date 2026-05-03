import { beforeEach, describe, expect, it, vi } from "vitest";

import * as api from "./api";

describe("postJob/getJob", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string | URL | Request, init?: RequestInit) => {
        const u = String(url);
        if (u.endsWith("/api/v1/jobs") && init?.method === "POST") {
          return new Response(JSON.stringify({ id: "jid-1", status: "pending", payload_json: {} }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }
        if (u.endsWith("/api/v1/jobs/jid-1")) {
          return new Response(JSON.stringify({ id: "jid-1", status: "success" }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }
        return new Response("not mocked", { status: 599 });
      }) as typeof fetch,
    );
  });

  it("uses configured base URL and JSON methods", async () => {
    const body = {
      intent: {
        sessionId: "x",
        promptOriginal: "p",
        intent: { objectType: "box", style: [], functionalGoal: "g" },
        constraints: {
          dimensionsMm: { width: 1, height: 2, depth: 3 },
          symmetry: "none",
          manufacturingHints: [],
          materialHints: [],
        },
      },
    };
    await api.postJob(body);
    await api.getJob("jid-1");
    expect(fetch).toHaveBeenCalled();
    expect(String((fetch as ReturnType<typeof vi.fn>).mock.calls[0][0])).toContain("http://stub.test");
  });
});
