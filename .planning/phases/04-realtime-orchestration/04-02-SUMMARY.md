---
phase: 04-realtime-orchestration
plan: "02"
subsystem: worker
tags:
  - celery
  - redis
  - realtime
requires:
  - phase: "04-realtime-orchestration"
    provides: "Canal Redis e contrato `schemaVersion 1`; API pode publicar `job.cancelled` em paralelo"
provides:
  - Publicador síncrico `publish`/`build_envelope` no worker
  - `process_geometry_job` emite todas as etapas PROMPTING → MEASURING_ABNT cooperativamente cancelável
affects:
  - realtime
tech-stack:
  added:
    - optional dev `fakeredis`
  patterns:
    - "Mesmo formato JSON da API (`jobId`, `detail.pipelineStage`, `detail.lifecycle`)"
key-files:
  created:
    - services/worker/src/neuralcad_worker/realtime.py
    - services/worker/tests/test_realtime_publish.py
  modified:
    - services/worker/src/neuralcad_worker/tasks/geometry.py
    - services/worker/src/neuralcad_worker/db/sync_session.py
key-decisions:
  - Duplicação benigna `job.cancelled` API/worker tratada pela UI pelo fecho após primeira mensagem terminal
patterns-established:
  - Reload de `jobs.status` entre etapas para cancelamento cooperativo
requirements-completed:
  - RT-01
  - RT-02
duration: 90min
completed: 2026-05-03
---

# Fase 04 — PLANO 02 (Wave 2) — SUMMARY

**Publisher centralizado no worker**: eventos JSON com `schemaVersion` 1, progresso obrigatório por etapa OCC stub e ciclo `job.lifecycle`; cancelamento antes de próxima etapa.

## Realizações

- `geometry.py`: sequência PROMPTING, DENOISING_FACES/EDGES, SEWING, MEASURING_ABNT com `_blocked_by_cancel` após `_progress`.

## Smoke testes

```bash
cd services/worker && PYTHONPATH=src .venv/bin/python -m pytest tests/test_realtime_publish.py -q
```

Instalação opcional:

```bash
cd services/worker && uv venv && uv pip install --python .venv/bin/python -e ".[dev]"
```

## Self-Check: PASSED

- Smoke `fakeredis` confirma `publish()` entrega mensagem tipo `job.lifecycle` no canal `neuralcad:job:{uuid}`.

