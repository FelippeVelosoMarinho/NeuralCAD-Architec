---
phase: 03-vs-code-like-ui-3d-foundation
gathered: 2026-05-03
status: Ready for execution
sources:
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - IDEA.md
  - services/api/src/neuralcad_api/main.py
---

# Phase 3 — Context

## Boundary

Entregar um **frontend monorepo (Vite + React + TypeScript)** alinhado a `IDEA.md` § *Closed Technical Stack* e § *UX Blueprint*: shell estilo VS Code (sidebar explorer, centro com editor/tab viewport, painel inferior copiloto), **Monaco** para o prompt, **Three.js / R3F** para pré-visualização da geometria gerada pelo backend já existente (Phase 1–2).

**Depends on Phase 2:** contratos `/api/v1/intent/elicit`, `/api/v1/jobs/{id}`, payload `IntentJobEnvelope`; worker grava STEP em MinIO e `artifact_key` em Postgres.

**Out of Phase 3:** WebSockets fluxo tempo-real (Phase 4), refinamento por picking (Phase 5).

## Locked decisions

| ID | Decision |
|----|----------|
| D-UI-01 | Novo pacote **`services/web/`** com Vite+React18+TS na raíz do mesmo repositório (padrão `services/api`, `services/worker`). |
| D-UI-02 | Estado global app shell: **Zustand**; dados remotos **`fetch` inicial** ou TanStack Query mínimo onde simplify polling de job até Phase 4. |
| D-UI-03 | Centro: **tabs** “Prompt (Monaco)” e “Viewport 3D” compartilhando largura máxima. |
| D-UI-04 | Artefaço STEP em MinIO não é consumível diretamente pelo Three sem WASM pesado; MVP: servidor expõe **download do STEP** (+ opcional **mesh STL**) e viewport usa **STL** via `THREE.STLLoader`; se só STEP existir, plano obriga tesselação lado worker ou segunda chave objeto (decisão no plano 03-03). |
| D-UI-05 | Árvore B-rep MVP: síncrono com modelo carregado / metadados de job (`dimensional_audit` + resumo topológico se exposto pelo worker). |

## Canonical references

- `IDEA.md` — UX Blueprint, stack fechado.
- `.planning/REQUIREMENTS.md` — UI-01 … UI-04.
- `services/api/` — URLs base API; será necessário **endpoint público para bytes do artefato** para o browser (presigned ou proxy streaming).

## Open questions (resolved in RESEARCH.md / PLANs)

- Formato de mesh servido ao browser (STL vs apenas STEP): ver `03-RESEARCH.md`.

---

*Phase 3 — vs-code-like-ui-3d-foundation*
