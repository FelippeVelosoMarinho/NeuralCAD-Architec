/**
 * NeuralCAD prompt-bridge: expõe HTTP para o Prompt Architect Python chamar Cursor via @cursor/sdk.
 */

import express from "express";
import { Agent, CursorAgentError } from "@cursor/sdk";

const PORT = Number(process.env.PORT ?? 3040);
const app = express();
app.use(express.json({ limit: "2mb" }));

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "neuralcad-prompt-bridge" });
});

app.post("/v1/complete", async (req, res) => {
  const prompt = req.body?.prompt;
  if (typeof prompt !== "string" || !prompt.trim()) {
    return res.status(400).json({
      error: "prompt must be a non-empty string",
    });
  }

  const apiKey = process.env.CURSOR_API_KEY?.trim();
  if (!apiKey) {
    return res.status(503).json({ error: "CURSOR_API_KEY is not set" });
  }

  const cwd =
    process.env.CURSOR_AGENT_CWD?.trim() || process.cwd();
  const modelId = (
    process.env.CURSOR_MODEL_ID || "composer-2"
  ).trim();

  try {
    const runResult = await Agent.prompt(prompt, {
      apiKey,
      model: { id: modelId },
      local: { cwd },
    });

    if (runResult.status === "error") {
      return res.status(502).json({
        error: "cursor_agent_run_failed",
        detail:
          runResult.result?.slice(0, 4000) ||
          "Agent finished with error status and no textual result.",
      });
    }

    const raw =
      typeof runResult.result === "string" ? runResult.result : "";
    if (!raw.trim()) {
      return res.status(502).json({
        error: "empty_result",
        detail:
          "Agent returned no text in result.result; widen prompt or inspect Cursor dashboard.",
      });
    }

    res.json({ raw });
  } catch (err) {
    if (err instanceof CursorAgentError) {
      return res.status(503).json({
        error: err.message,
        retryable: err.isRetryable,
      });
    }
    console.error("prompt-bridge unexpected error", err);
    res.status(500).json({
      error: "internal_error",
      detail: String(err?.message || err),
    });
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`neuralcad-prompt-bridge listening on :${PORT}`);
});
