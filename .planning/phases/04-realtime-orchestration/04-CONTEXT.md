---
phase: realtime-orchestration
slug: realtime-orchestration
status: active
depends_on_phase: "03-vs-code-like-ui-3d-foundation"
created: 2026-05-03
---

# Phase 4 — Context (`04-realtime-orchestration`)

## Objetivo (ROADMAP)

Experiência contínua desde o prompt até à geometria disponível, com **atualização em tempo real** no browser em vez de polling exclusivo a 2 s (**RT-01…RT-03**).

## Estado actual do código

- **UI:** `useJobFlow` faz **polling** `GET /api/v1/jobs/{id}` a cada 2 s (Phase 3 deixou WebSocket fora de propósito).
- **API:** FastAPI + Celery `process_geometry_job`; modelo `Job` com `status`, `payload_json`, `artifact_key`, `dimensional_audit`.
- **Worker:** `services/worker/.../geometry.py` processa job e grava Postgres/MinIO.
- **Sem** canal WebSocket, **sem** pub/sub explícito worker→API (além do broker Celery/Redis).

## Decisões de desenho (MVP Phase 4)

1. **Transporte:** `WebSocket` FastAPI (`/ws/jobs/{job_id}`). **Sessão MVP:** UUID `client_session` em query string — sem OAuth; documentar.
2. **Fan-out:** **Redis Pub/Sub** canal `neuralcad:job:{job_id}` — cada conexão WS subscreve; worker **publica** em transições de estado.
3. **UI:** **TanStack Query** para cache do job + eventos WS invalidam ou actualizam estado; reduzir/remove `setInterval` de polling.
4. **Reconexão:** backoff no cliente; ao abrir WS fazer um **GET** do job como fonte de verdade inicial.

## Fora de escopo

Multi-utilizador (V2), streaming binário STEP/STL pelo WS.

## Próximo passo GSD

- Opcional: `/gsd-discuss-phase 4`
- Execução: `/gsd-execute-phase 4` ou ondas individuais `04-01` → `04-02` → `04-03`
