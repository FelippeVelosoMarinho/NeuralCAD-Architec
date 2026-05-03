---
phase: 02
slug: intent-schema-prompt-architect
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-03
---

# Phase 02 — Validation Strategy

> Contrato Nyquist/Dimension 8: amostragem após cada tarefa e onda quando testes automatizados existem.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `services/api/pyproject.toml` (optional-deps dev) |
| **Quick run command** | `cd services/api && python -m pytest -q --tb=short tests/test_intent_schema.py` |
| **Full suite command** | `cd services/api && python -m pytest -q --tb=short` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Quick run no ficheiro de teste mais próximo do plano
- **After every plan wave:** Full suite em `services/api/tests/`
- **Before `/gsd-verify-work`:** Full suite verde
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|---------------|------------|------------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | INTENT-01 | T-PA-01 | Sem `extra=allow` no modelo publicado | unit | `pytest tests/test_intent_schema.py -q` | ⬜ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | INTENT-01 | — | Fixtures sem segredos | unit | `pytest tests/test_intent_schema.py -q` | ⬜ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | INTENT-02 | T-PA-02 | API key só via env | unit | `pytest tests/test_prompt_architect.py -q` | ⬜ W0 | ⬜ pending |
| 02-02-02 | 02 | 2 | INTENT-04 | — | Logs sem prompt completo em produção opcional | unit | `pytest tests/test_prompt_architect.py -q` | ⬜ W0 | ⬜ pending |
| 02-03-01 | 03 | 3 | INTENT-03 | — | Payload validado antes de enqueue | integration | `pytest tests/test_jobs_intent_flow.py -q` | ⬜ W0 | ⬜ pending |
| 02-03-02 | 03 | 3 | INTENT-01 | — | JobCreate sem campos extra | integration | `pytest tests/test_jobs_intent_flow.py -q` | ⬜ W0 | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `services/api/tests/conftest.py` — fixtures app + override DB opcional
- [ ] `services/api/tests/test_intent_schema.py` — contrato INTENT-01
- [ ] `pytest` em `[project.optional-dependencies] dev`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|---------------------|
| Chamada real Claude | INTENT-02 | Custo + API key | Com `ANTHROPIC_API_KEY` definido, `curl` `POST /api/v1/intent/elicit` com prompt vago e verificar clarificação |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity maintained
- [ ] `nyquist_compliant: true` após execução

**Approval:** pending
