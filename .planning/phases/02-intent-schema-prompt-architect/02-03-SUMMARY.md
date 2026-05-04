---
phase: 02-intent-schema-prompt-architect
plan: "03"
subsystem: api
tags: [fastapi, pydantic, intent-schema, celery, docker-compose]

requires:
  - phase: 02-intent-schema-prompt-architect
    provides: schemas intent v1, Prompt Architect, elicitation types
provides:
  - IntentJobEnvelope strict + retry com normalização legada (dims sob intent interno → constraints)
  - POST /api/v1/jobs com persistência preflight em payload_json
  - Testes test_jobs_intent_flow (schemas + TestClient com DB mock)
  - Compose e README com fluxo elicit → jobs
affects: [worker-geometry-dims, fase-03]

tech-stack:
  added: []
  patterns:
    - "Retry único: validate envelope → normalize_legacy → validate"
    - "payload_json canónico = model_dump(IntentSchemaV1) + preflight opcional + schemaVersion"

key-files:
  created:
    - services/api/tests/test_jobs_intent_flow.py
  modified:
    - services/api/src/neuralcad_api/services/payload_normalize.py
    - docker-compose.yml
    - README.md

key-decisions:
  - "Normalização remove ``constraints`` errado no IntentBlock após promover dimensionsMm para ``constraints`` do IntentSchema."
  - "Não gravar schemaVersion na raiz do envelope JSON; apenas em persist_payload_from_envelope."

patterns-established:
  - "Heurística envelope: ``intent`` com sessionId/promptOriginal → corrigir só o sub-documento e limpar constraints na raiz do body."

requirements-completed: [INTENT-01, INTENT-02, INTENT-03, INTENT-04]

duration: ""
completed: 2026-05-03
---

# Fase 2 — Plano 03: HTTP jobs + normalização legada

**Envelope de job estrito (`IntentJobEnvelope`), normalização que promove ``dimensionsMm`` a partir do caminho legado ``intent.constraints`` no bloco interno, persistência de ``preflight.geo_risk`` e regressão coberta por testes.**

## Performance

- **Tarefas:** 3 (normalização/schemas, rotas/main/compose/README, worker já alinhado + testes)
- **Ficheiros principais:** `payload_normalize.py`, `test_jobs_intent_flow.py`, `docker-compose.yml`, `README.md`

## Accomplishments

- Correcção da normalização para não invalidar `IntentJobEnvelope` (`extra=forbid`) e eliminar campos proibidos no `IntentBlock` após promoção.
- Suite `pytest` em `services/api/tests/` com 11 testes a passar.
- `docker compose config` válido com `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` no serviço `api`.

## Decisions Made

- `schemaVersion` fica apenas no `payload_json` persistido (`persist_payload_from_envelope`), não no dict de entrada do envelope.

## Deviations from Plan

None — o plano pedia retry após normalização mínima; a implementação alinha o shape do envelope removendo `constraints` órfãs na raiz e o bloco legado dentro de `intent`.

## Issues Encountered

- Ambiente local com SQLAlchemy 1.4 do sistema exigiu upgrade para 2.x para correr testes que importam `main.py`.

## Verification

- `cd services/api && PYTHONPATH=src python3 -m pytest -q tests/`
- `docker compose config -q` na raíz do repositório `app`

## Next Phase Readiness

- API aceita intents validados + snapshot de preflight; worker já lê `constraints.dimensionsMm` antes do fallback legado no `intent`.

---
*Phase: 02-intent-schema-prompt-architect*
*Completed: 2026-05-03*
