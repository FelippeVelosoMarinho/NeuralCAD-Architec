# Phase 1: Geometric pipeline & platform - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `01-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-05-03
**Phase:** 1 — Geometric pipeline & platform
**Areas discussed:** Ponte dimensional IntentSchema ↔ pythonocc (foco via `--context`); ordem do pipeline e persistência

---

## IntentSchema (target) vs pythonocc (as-built)

| Option | Description | Selected |
|--------|-------------|----------|
| Apenas bbox de debug sem persistência | Rápido, mas não audita fidelidade ao intent |  |
| **Audit JSONB + delta + tolerância explícita** | Medição sempre persistida; comparação quando target existe; não bloqueia job na F1 | ✓ |
| Gate duro (falhar job se fora tolerância) | Mais “CAD certo”, mas atrasa protótipo e mistura preocupação da Fase 2 |  |

**User's choice:** Diretriz explícita em `--context`: focar na integração IntentSchema ↔ extração OCC para **fidelidade dimensional** no protótipo — interpretado como coluna do meio (auditoria + tolerância como **report**, não falha).

**Notes:** Fluxo unconditional da Fase 1 continua válido: `measured` sem `target`. Espessura como medida opcional no protótipo.

---

## Onde executar medição OCC

| Option | Description | Selected |
|--------|-------------|----------|
| Script manual pós-job | Não integra com FOUND |  |
| **Worker pós-geração, pré-status success** | Garante todo artefato versionado tem audit | ✓ |
| Serviço micros serviço separado só para métricas | Mais complexidade operacional na F1 |  |

**User's choice:** Worker unificado (recomendado para protótipo).

---

## Claude's Discretion

- Nomes exatos de endpoints e helpers OCC — planner decide dentro dos contratos D-01..D-08.

## Deferred Ideas

- Lint geométrico completo e gates de qualidade duros — fases posteriores.
