---
phase: 04-realtime-orchestration
plan: "01"
subsystem: api
tags:
  - fastapi
  - websocket
  - redis
  - celery
requires:
  - phase: 03-vs-code-like-ui-3d-foundation
    provides: "Cliente HTTP e uso de jobs na UI onde o realtime se integra"

provides:
  - Gateway WS `/ws/jobs/{job_id}` com Redis pub/sub canal `neuralcad:job:{id}`
  - DELETE cancelável com `revoke` e eventos lifecycle/cancel Redis
  - Persistência `celery_task_id` no job ao enfileirar
affects:
  - ui
tech-stack:
  added: []
  patterns:
    - "Envelope schemaVersion `1` sobre Redis + eco `channel.ready` com `clientSession` obrigatório na query WS"
key-files:
  created:
    - services/api/src/neuralcad_api/realtime_envelope.py
    - services/api/src/neuralcad_api/services/redis_bus.py
    - services/api/src/neuralcad_api/ws/job_channel.py
    - services/api/alembic/versions/002_job_celery_task_id.py
    - services/api/tests/test_jobs_realtime.py
  modified:
    - services/api/src/neuralcad_api/db/models.py
    - services/api/src/neuralcad_api/main.py
key-decisions:
  - "`client_session` UUID obrigatório na query WS; caso contrário ligação fechada antes de `accept`"
  - "Redis ausente permite API subir; WS recusa handshake com erro explícito"
patterns-established:
  - "Publicação JSON unificada via `publish_json` + envelopes tipados (`lifecycle`, `progress`, `cancelled`)"
requirements-completed:
  - RT-01
  - RT-03
duration: 120min
completed: 2026-05-03
---

# Fase 04 — PLANO 01 (Wave 1) — SUMMARY

**Superfície API tempo real**: WebSocket multiplexado pelo Redis Pub/Sub, cancelamento Celery correlacionado ao `DELETE /api/v1/jobs/{id}` e gravação de `celery_task_id` quando o job é criado.

## Realizações

- Migração + modelo `jobs.celery_task_id`; `DELETE` público em não terminais (409 coerentes em estado terminal).
- Rota WS com primeiro frame `channel.ready` e forwarding de texto do canal nomeado por job.
- Smoke `pytest`: `DELETE` pending → `cancelled` + revoke; WS sem sessão falha handshake; handshake com `fakeredis.aioredis` recebe segundo frame após `publish` tardio correto na subscrição ativa.

## CURL (exemplo)

```bash
# Cancelar job ainda pendente/correndo
curl -sS -X DELETE "http://127.0.0.1:8010/api/v1/jobs/{JOB_ID}"

# Upgrade WS — rota efectiva `/ws/jobs/{job_id}` (sem `/api/v1`)
CLIENT_SESSION="$(python3 -c 'import uuid; print(uuid.uuid4())')"
websocat "ws://127.0.0.1:8010/ws/jobs/{JOB_ID}?client_session=${CLIENT_SESSION}"
```

## Desvios

- Caminho WS sem prefixo `/api/v1`; alinha com inclusão direta via `FastAPI.include_router(job_ws_router)`.

## Self-Check: PASSED

- `PYTHONPATH=src uv run pytest services/api/tests/test_jobs_realtime.py -q`

