---
phase: 03-vs-code-like-ui-3d-foundation
kind: research
status: completed
completed: 2026-05-03
researcher: orchestrator-inline
---

# Phase 3 — Research

## Goal alignment

Construir **`services/web`** alinhado a `IDEA.md`: React 18 + Vite + TypeScript + Zustand + Three.js/R3F, Monaco Editor, layout shell estilo VS Code.

## Stack choices

| Piece | Recommendation | Notes |
|-------|----------------|-------|
| Bundler/dev | **Vite 6** | Alinhamento com PROJECT.md stack. |
| UI layout | Flexbox + CSS variáveis | Evitar libs layout pesadas no MVP; `react-resizable-panels` opcional para dividir centro. |
| Editor | **`@monaco-editor/react`** | Lazy load Monaco para não bloquear FCP. |
| 3D | **`@react-three/fiber`** + **`@react-three/drei`** (helpers orbit controls) | Padrão comunitário estável para React + Three. |
| Fetch layer | **`@tanstack/react-query`** opcional já em 03-02 para polling `/jobs/{id}` | Prepara Phase 4; polling simples com `useEffect` aceitável se reduz deps. |

## Artefacts & viewers

### Situação atual (backend)

- Worker grava **STEP** em MinIO sob `artifact_key` (`.step`).
- APIs expõem estado do job incluindo `artifact_key`; **download HTTP direto pelo browser pode não existir** — obrigatório adicionar rota REST que faça streaming ou redirect assinado.

### STEP vs STL no navegador

- **THREE.js não lê STEP nativamente.** Parsers STEP WASM (OpenCascade.js) aumentam bastante pacote/tempo build.
- **MVP pragmático:**
  1. **API `GET /api/v1/jobs/{id}/artifact`** (tipo `application/STEP` ou `octet-stream`) para download bruto — útil mesmo sem viewer.
  2. Viewer R3F: carregar **`STL`** com `THREE.STLLoader` (binário ascii suportável).
  3. **Worker** passa também a gerar **`model.stl`** (mesh triangular) lado servidor (pythonocc STL export ou teselação bbox) persistido paralelamente ao STEP para o mesmo `job_id`.

> Decisão de implementação ficará explícita em **03-03-PLAN** (tesselar STL mínimo no worker **ou** export STL existente OCC).

### Explorer topológico

- Para paralelipípedo/cubo stub atual, OCC pode expor contagens Faces/Edges/Vertices.
- Plano deve acrescentar `topologySummary` dentro de **`dimensional_audit`** (estrutura JSON estável consumida pela UI).

## Security (browser)

- CORS: frontend em dev (`5173`) chama API `8000` — configurar **`CORSMiddleware`** FastAPI com origins dev ou proxy Vite **`server.proxy`/preview**.
- Artefactos: preferir URLs autenticadas em produção — MVP permissivo apenas em dev compose.

## Risks

| Risk | Mitigation |
|------|-------------|
| Bundle size Monaco+R3F | Code-splitting routes/tabs lazy. |
| Polling flood | Backoff exponencial em `react-query`/hook manual. |
| Topo tree diverge OCC | Fixture documentado (“artefato de teste”) + estruturas derivadas de `dimensional_audit`. |

---

## Validation Architecture

A fase exige regressão rápida local:

- **`vitest` + `@testing-library/react`** para shells e hooks (stores, parse de topo).
- **Playwright opcional Wave 3** smoke (abrir página, clicar tabs) — postergável se infra CI ausente.

Estratégia detalhada em **`03-VALIDATION.md`**.

## RESEARCH COMPLETE

Documento pronto para alimentação do planner (`PLAN.md`).
