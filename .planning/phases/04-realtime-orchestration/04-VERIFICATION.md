---
status: passed
phase: 04-realtime-orchestration
reviewed: 2026-05-03
---

# Verificação — Fase 4: Realtime orchestration

## Objetivo do roadmap

Progresso em tempo real dos jobs através de Redis → WebSocket, cancelação correlacionada com Celery, e SPA com TanStack Query sem polling custoso sobre `GET /jobs/{id}`.

## Must-haves verificados (RT-01 … RT-03)

| ID | Critério | Evidência |
|----|----------|-----------|
| RT-01 | Canal job + WS + cancel worker/API | ```41:93:services/api/src/neuralcad_api/ws/job_channel.py```, ```101:173:services/api/src/neuralcad_api/main.py```, ```73:205:services/worker/src/neuralcad_worker/tasks/geometry.py``` |
| RT-02 | Eventos estágio OCC + lifecycle | `_progress`, `_lifecycle`, `build_envelope` em worker `geometry.py` e `realtime.py` |
| RT-03 | SPA sem intervalo GET; `client_session` | ```69:277:services/web/src/hooks/useJobFlow.ts```, ```1:17:services/web/src/lib/tabClientSession.ts```, ```1:14:services/web/src/lib/wsJobChannel.ts``` |

## Conformidade com planos

- **04-01:** modelo + Alembic `celery_task_id`, envelopes API, DELETE + revoke, handshake WS obrigatório `client_session`, smoke `pytest` `tests/test_jobs_realtime.py`.
- **04-02:** `publish(job_id, envelope)`, cancelamento cooperativo entre etapas, etapas exigidas no CONTEXT, teste fakeredis opcional worker `tests/test_realtime_publish.py`.
- **04-03:** Bootstrap React Query (`main.tsx`), URL WS desde `env`, teste Vitest `wsJobChannel`, etapa no painel `App.tsx`.

## Testes automáticos (executados)

- `PYTHONPATH=src uv run pytest services/api/tests/ -q` — 21 passes.
- `npm test -- --run` (`services/web`) — 4 passes.
- Opcional isolado worker: `.venv/bin/python -m pytest services/worker/tests/test_realtime_publish.py`.

## Verificação humana (não bloqueante)

1. Compose com Redis vivo: fluxo criar job + ver progresso SSE-like no browser.
2. Cenário “duas abas partilham jobId” depende do produto expor mesmo ID — ver nota em `04-03-SUMMARY.md`.

## Regressão

- Testes Phase 03 front (`App.test`) corrigidos com `QueryClientProvider`.
- Fixture Celery intent flow usa `MagicMock` para garantir chamada registada ao `send_task`.

## Conclusão

**status: passed** — contratos realtime e automação disponíveis cobrem os must-haves; UAT navegador deixado como complemento opcional quando Redis/Docker disponíveis.
