---
phase: 04-realtime-orchestration
plan: "03"
subsystem: ui
tags:
  - tanstack-query
  - websocket
  - vite
requires:
  - phase: "04-realtime-orchestration"
    provides: "WS canal job + envelopes progress/lifecycle/cancelled"
provides:
  - `useJobFlow` sem polling; GET único pós-erro antes de novo socket (até ao limite de tentativas)
  - UUID `client_session` por aba persistido em `sessionStorage`
  - Etapa de engenharia em texto derivada de último `job.progress.pipelineStage`
affects:
  - ui
tech-stack:
  added:
    - "@tanstack/react-query"
key-files:
  created:
    - services/web/src/lib/tabClientSession.ts
    - services/web/src/lib/wsJobChannel.ts
    - services/web/src/hooks/queryKeys.ts
    - services/web/src/lib/wsJobChannel.test.ts
  modified:
    - services/web/src/hooks/useJobFlow.ts
    - services/web/src/main.tsx
    - services/web/src/App.tsx
    - services/web/package.json
key-decisions:
  - Reconectar após erro WS segue CONTEXT: primeiro `fetchQuery` snapshot antes de novo `WebSocket`
patterns-established:
  - Chave estável TanStack Query `jobDetailKey(id)` espelho do snapshot do job
requirements-completed:
  - RT-02
  - RT-03
duration: 90min
completed: 2026-05-03
---

# Fase 04 — PLANO 03 (Wave 3) — SUMMARY

**SPA sem intervalo**: abertura de WS obrigatória com `client_session`, invalidação/consulta após eventos terminais, rótulo de etapa OCC bruto no UI.

## Desvios

- `App.test.tsx` atualizado para `QueryClientProvider` local (mirror de `main.tsx`).

## UAT manual (duas abas / mesmo jobId)

1. Servir API + SPA; numa aba criar job; copiar ID.
2. Abrir segunda aba ligada ao mesmo `jobId`/fluxo esperado apenas se usar endpoint GET partilhado — fluxo habitual gera novo job por aba por convenção atual; PLAN pedia cenário opcional quando jobId partilhado via URL/handoff (marcar pendente até produto definir navegação partilhada).

## Auto check

```bash
cd services/web && npm test -- --run
```

## Self-Check: PASSED

- Vitest verde inclusive `wsJobChannel` constrói URL com query `client_session`.

