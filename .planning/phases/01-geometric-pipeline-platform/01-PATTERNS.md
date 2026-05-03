# Phase 01 — Pattern map (greenfield)

**Gerado:** 2026-05-03  
**Nota:** Repositório sem código prévio; este ficheiro análogo serve para o executor alinhar com `.planning/phases/01-geometric-pipeline-platform/01-CONTEXT.md`.

## Ficheiros a criar (papéis)

| Ficheiro / pasta | Papel | Analogia (conceptual) |
|-------------------|-------|------------------------|
| `docker-compose.yml` | Orquestração local FOUND-01 | Padrão Compose multi-service |
| `services/api/` | FastAPI + rotas HTTP + modelos DB | App síncrona + SQLAlchemy/async |
| `services/worker/` | Celery + tarefas + OCC | Worker GPU/CPU com fila |
| `packages/schemas/` (opcional) | Pydantic partilhado (job, `dimensional_audit`) | Contrato API/worker |
| `.env.example` | Variáveis sem segredos | Documentação de env |

## Fluxo de dados

`POST /jobs` → Postgres (pendente) → Redis broker → Celery task → (stub geométrico ou BrepGen futuro) → MinIO (STEP) → medição OCC → JSONB `dimensional_audit` → estado `success`.

## Extratos

_Não aplicável — codebase vazio._
