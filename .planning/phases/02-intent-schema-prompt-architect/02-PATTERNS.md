# Phase 02 — Pattern map

## Files to add / modify (from CONTEXT + RESEARCH)

| File | Role | Closest analog in repo |
|------|------|------------------------|
| `services/api/src/neuralcad_api/schemas/jobs.py` | Request/response job | Existente `JobCreate` — substituir padrão por modelos strict |
| `services/api/src/neuralcad_api/main.py` | Rotas FastAPI | Padrão actual `create_job` / `get_job` |
| `services/api/src/neuralcad_api/db/models.py` | Entidade `Job` | Já tem `payload_json` JSONB |
| `services/worker/.../geometry.py` | Parse dims | `_parse_target_dims` existente |
| Novo `schemas/intent_v1.py` | Domínio | Nenhum — primeiro módulo de domínio NL↔geom |
| Novo `services/prompt_architect.py` | Cliente LLM | Nenhum — novo serviço |

## Excerpts a replicar

- **Dependency injection:** `Depends(get_db)` como em `main.py`
- **Celery:** `celery_app.send_task("process_geometry_job", args=[str(job.id)])` inalterado após job persistido
- **Environ:** seguir `os.environ` / `.env.example` como Compose actual

## Data flow

`NL → POST /intent/elicit → (Claude) → IntentSchemaV1 + geo_risk → POST /jobs → payload_json + preflight → Celery → worker lê constraints + generationConfig`

## PATTERN MAPPING COMPLETE
