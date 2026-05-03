# NeuralCAD Architect

## What This Is

NeuralCAD Architect é um co-piloto CAD nativo de IA que converte intenção arquitetônica em linguagem natural (muitas vezes vaga) em geometria B-rep válida e editável, com um fluxo iterativo guiado por especificação. Combina **BrepGen** como motor de geração geométrica, **Claude** como arquiteto de prompts (Prompt Architect) e uma interface multimodal inspirada em VS Code (Monaco, barras laterais, viewport 3D).

## Core Value

Um usuário descreve o que precisa em linguagem natural e recebe **candidatos B-rep válidos (STEP/STL)** com rastreabilidade, feedback de qualidade geométrica e controle iterativo — sem depender de um operador CAD experiente para traduzir cada intenção em operações de baixo nível.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Pipeline backend gera B-rep de forma assíncrona (API + workers) com artefatos versionados
- [ ] Contrato **IntentSchemaV1** entre LLM e motor geométrico, com validação e clarificações mínimas
- [ ] Shell de UI estilo VS Code: explorer de topologia, Monaco, viewport 3D, console copiloto
- [ ] Loop tempo real: prompt → geração → atualização de modelo na UI
- [ ] Refinar por seleção (face/edge/vertex), lint geométrico, histórico e diff visual entre iterações
- [ ] Stack fechada do MVP conforme `IDEA.md` (FastAPI, Celery, Redis, Postgres 16, MinIO, React/Vite, Three.js, Docker Compose)

### Out of Scope

- Suíte CAD completa substituindo SOLIDWORKS/CATIA — foco em co-piloto de conceito/refino
- Paridade de montagem multi-corpo com CAD enterprise na v1
- Colaboração multi-usuário em tempo real
- Retreino customizado do BrepGen na primeira release

## Context

- **Problema:** ciclo ideia→geometria lento; intenção subespecificada; falhas de topologia em iteração manual.
- **Usuários-alvo:** arquitetos, designers industriais, engenheiros CAD mecânico, times que constroem ferramentas de autorização assistida por IA.
- **Orquestração de IA:** Claude deve sempre extrair intenção, normalizar para `IntentSchemaV1`, validar ambiguidade, emitir config pronta para BrepGen e explicar riscos antes de gerar.
- **Métricas de sucesso (produto):** taxa de solidos válidos (watertight), latência prompt→primeiro modelo aceitável, taxa de sucesso em refinamento, redução de voltas de clarificação, sensação de controle.

## Constraints

- **Tech stack (MVP):** Backend Python 3.10, FastAPI, Pydantic v2, Celery + Redis, PostgreSQL 16, MinIO; CAD/B-rep: PyTorch 2.2, Diffusers 0.27, BrepGen, pythonocc-core, occwl; Frontend React 18 + TS + Vite, Three.js + R3F, Zustand, TanStack Query, WebSockets; qualidade: pytest, vitest, playwright, ruff, black, eslint, prettier; observabilidade: OpenTelemetry + Prometheus + Grafana; runtime Docker Compose + Nginx.
- **Contrato canônico:** saída estruturada alinhada a **IntentSchemaV1** (ver `IDEA.md`).
- **Dependência de modelo:** geração geométrica depende de BrepGen e do pipeline descrito no brief; latência e fila assíncrona são explícitas no desenho.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Stack fechada no MVP (`IDEA.md`) | Reduz decisões tardias e alinha equipe num único alvo | — Pending |
| IntentSchemaV1 como contrato único | Separa NL de geometria e permite validação automatizada | — Pending |
| UI inspirada em VS Code | Familiaridade para devs e fluxo editor + painéis + terminal/coploto | — Pending |
| Fila assíncrona (Celery + Redis) | Geração pesada não bloqueia API; UX de progresso via WS | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-03 after initialization*
