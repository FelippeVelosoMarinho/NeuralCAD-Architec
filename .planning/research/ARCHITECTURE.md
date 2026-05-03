# Architecture Research

**Domain:** AI CAD co-pilot (B-rep)
**Researched:** 2026-05-03
**Confidence:** MEDIUM-HIGH (padrão arquitetural; detalhes de deployment na implementação)

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Client (React + Vite)                    │
│  Sidebar tree │ Monaco │ Viewport (Three/R3F) │ Copilot panel │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP + WebSocket
┌───────────────────────────▼─────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  REST: sessões, intents, jobs │ WS: progresso / eventos       │
└───────┬───────────────────────────────┬─────────────────────┘
        │                                 │
        ▼                                 ▼
┌───────────────┐                 ┌───────────────────┐
│ Redis (broker)│◄───────────────►│ Celery workers   │
└───────┬───────┘                 │ BrepGen + OCC    │
        │                         └─────────┬─────────┘
        ▼                                   │
┌───────────────┐                             │
│ PostgreSQL 16 │◄── metadados ───────────────┘
└───────────────┘
        │
        ▼
┌───────────────┐
      MinIO     │ ◄── STEP / STL / diffs
└───────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|-------------------------|
| Prompt Architect | NL → IntentSchemaV1, clarificações | Claude via API, validação Pydantic |
| Generation service | Intent validado → job BrepGen | Celery task, GPU opcional |
| Geometry services | Lint, repair leve, export | pythonocc-core / occwl |
| Realtime gateway | Assinaturas de job | FastAPI WebSockets |
| UI presentation | Shell IDE + picking | React, Zustand, Query |

## Recommended Project Structure (suggested)

```
/services/api          # FastAPI app
/services/worker       # Celery consumers + BrepGen
/packages/schemas      # IntentSchemaV1 compartilhado (Python + optional TS types)
/apps/web              # Vite React frontend
/infra                 # Docker Compose, Nginx, observabilidade
```

## Data Flow

1. Usuário edita prompt no Monaco → envia ao backend.
2. API chama **Prompt Architect** → `IntentSchemaV1` validado ou perguntas de esclarecimento.
3. API enfileira job → worker gera B-rep → persiste artefato MinIO + registro Postgres.
4. Eventos de progresso → WS → UI atualiza viewport e lint.

## Suggested Build Order

1. Worker + API mínimos e geração incondicional (prova de valor geométrica).
2. Contrato Intent + loop de validação LLM.
3. Shell UI + viewport estático/carregamento de arquivo.
4. WS + fluxo ponta a ponta na UI.
5. Seleção, refinamento, diff e lint na experiência completa.

---
*Ordem correlaciona com fases do ROADMAP.*
