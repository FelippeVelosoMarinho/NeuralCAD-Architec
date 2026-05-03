# Stack Research

**Domain:** AI-native CAD / generative B-rep authoring
**Researched:** 2026-05-03
**Confidence:** MEDIUM (aligned to project-locked stack in `IDEA.md`; versions should be pinned at implementation time against upstream docs)

## Recommended Stack

### Core Technologies

| Technology | Version (target) | Purpose | Why Recommended |
|------------|------------------|---------|----------------|
| Python | 3.10 | Backend + ML glue | Ecossistema OCC/BrepGen e async workers maduros |
| FastAPI | latest stable | HTTP API | Tipagem Pydantic v2, OpenAPI, async |
| Pydantic | v2 | Schemas / IntentSchemaV1 | Validação e contratos LLM↔backend |
| Celery + Redis | current stable | Jobs de geração | Desacopla latência de inferência e OCC |
| PostgreSQL | 16 | Metadados sessões, jobs, versionamento | ACID, consultas relacionais |
| MinIO | S3-compatible | STEP/STL/diffs | Objetos grandes fora do DB |
| PyTorch | 2.2 | BrepGen runtime | Dependência declarada do motor |
| Diffusers | 0.27 | Pipeline declarativa | Alinhado ao brief |
| BrepGen | (project pin) | Geração B-rep | Motor escolhido pelo produto |
| pythonocc-core + occwl | (pin) | Validação / lint / util OCC | Base industrial para B-rep |
| React + TypeScript | 18 / 5.x | UI | Ecosistema e hiring |
| Vite | current | Build frontend | DX rápida |
| Three.js + R3F | current | Viewport 3D | Padrão web para malhas/B-rep tessellado |
| Zustand + TanStack Query | current | Estado cliente + server cache | Encaixa shell tipo IDE |
| WebSockets | via FastAPI | Progresso job / streaming eventos | UX tempo real |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pytest / vitest | Testes backend / frontend | Cobrir contratos IntentSchema e API |
| Playwright | E2E | Fluxos críticos UI ↔ API |
| ruff / black / eslint / prettier | Estilo | Gate de CI cedo |
| OpenTelemetry + Prometheus + Grafana | Observabilidade | Essencial com fila + GPU |

### What NOT to Use

- **Substituir OCC/BrepGen por CAD desktop headless genérico na v1** — explode escopo e licenciamento.
- **Sincronizar estado só por polling** para geração longa — WS ou SSE é table stakes para UX.
- **Guardar blobs grandes no Postgres** — MinIO/objeto é mais simples e barato.

## Alternatives Considered

| Locked choice | Alternative | When to Use Alternative |
|---------------|-------------|-------------------------|
| Celery | RQ / Dramatiq | Menor operações; Celery se escalabilidade e ecossistema forem prioridade |
| MinIO | S3 cloud direto | Produção cloud gerenciada no deploy final |
| Zustand | Redux | Estado muito formal; Zustand casa melhor com layout IDE |

## Installation

```bash
# Será detalhado na Fase 1 — placeholders alinhados ao monorepo planejado
# docker compose up — serviços: api, worker, redis, postgres, minio, frontend
```

---
*Stack locked por decisão de produto; revalidar versões na primeira execução de dependências.*
