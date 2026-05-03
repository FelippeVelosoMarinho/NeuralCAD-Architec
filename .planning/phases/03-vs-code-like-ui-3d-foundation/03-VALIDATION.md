---
phase: 03-vs-code-like-ui-3d-foundation
slug: vs-code-like-ui-3d-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-03
---

# Phase 3 — Validation Strategy

> Feedback sampling durante execução da fase (shell + Monaco + viewport).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest + Testing Library (`@testing-library/react`) |
| **Config file** | `services/web/vitest.config.ts` (criado Wave 1) |
| **Quick run command** | `cd services/web && npm run test` |
| **Full suite command** | `cd services/web && npm run test -- --run` |
| **Estimated runtime** | ~15 seconds |

Backend regressões existentes continuam em `services/api` (`pytest`).

---

## Sampling Rate

- **Depois do merge de cada PLAN:** rodar comando rápido `vitest`.
- **Antes `/gsd-verify-work` nesta fase:** full suite frontend + pytest API.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|--------|
| 03-01-01 | 01 | 1 | UI-01 | T-UI-01 | Sandbox DOM only | vitest smoke | `cd services/web && npm run test` | ⬜ pending |
| 03-02-01 | 02 | 2 | UI-02 | T-UI-02 | Secrets só via env `.env`; sem keys no bundle | vitest cliente API mock | `cd services/web && npm run test` | ⬜ pending |
| 03-03-01 | 03 | 3 | UI-03 · UI-04 | T-UI-03 | Mesh sem `eval`; URLs artefato apenas API | vitest parsers + opcional playwright | `cd services/web && npm run test` | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `services/web/vite.config.ts` + `vitest.setup.ts` (se necessário)
- [ ] `services/web/src/test-utils.tsx` — wrapper providers mínimos
- [ ] Scripts `test`, `lint` em `services/web/package.json`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual |
|----------|--------------|-------------|
| Navegar layout não corrompe estado global | UI-01 | Checagem visual / click-through não coberta só por snapshots |
| Orbit viewport + mesh visível artefato real | UI-03 | Requer Compose + dados MinIO gerados pelo worker |

---

## Validation Sign-Off

- [ ] Todas as tasks `<automated>` ou marcadas explicitly manual-only
- [ ] `wave_0_complete: true` após scaffold de vitest na Wave 1
- **Approval:** pending
