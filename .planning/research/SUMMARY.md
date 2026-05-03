# Project Research Summary

**Project:** NeuralCAD Architect
**Domain:** AI-native CAD co-pilot (B-rep)
**Researched:** 2026-05-03
**Confidence:** MEDIUM

## Executive Summary

NeuralCAD Architect posiciona-se na fronteira entre **autorização CAD assistida por LLM** e **geração volumétrica/topológica via BrepGen**, com forte ênfase em **contrato estruturado** (IntentSchemaV1) e **transparência** (lint, explicações, diffs). A pesquisa confirma que o diferencial não é só “gerar malha”, mas **fechar o loop** entre intenção subespecífica, validação, refinamento por seleção e histórico auditável.

O stack do MVP está **deliberadamente fechado** no brief do produto: serviços Python async, fila de trabalhos, armazenamento de objetos, e um cliente React estilo IDE. Os principais riscos são **ambiguidade semântica**, **topologia frágil após edições locais** e **latência de geração** — todos endereçáveis por schema rígido, lint/rollback e UX assíncrona.

## Key Findings

### Recommended Stack

Resumo: FastAPI + Celery + Redis + Postgres + MinIO no backend; BrepGen + OCC no worker; React/Vite + Three/R3F no cliente; observabilidade com OpenTelemetry.

**Core technologies:**
- **FastAPI + Pydantic v2:** contratos HTTP e IntentSchema — validação determinística
- **Celery + Redis:** desacoplar geração pesada da API
- **MinIO:** artefatos grandes e diffs fora do relacionamento
- **React + Three.js:** shell familiar + viewport web

### Expected Features

**Must have (table stakes):**
- NL → candidato B-rep com export comum (STEP/STL)
- Jobs assíncronos com visibilidade de progresso
- Validação / lint geométrico básico

**Should have (competitive):**
- IntentSchemaV1 + clarificações mínimas
- Refino por seleção e diff visual entre iterações

**Defer (v2+):**
- Colaboração multi-usuário realtime
- Paridade de montagem enterprise

### Architecture Approach

Monólito modular em serviços: API síncrona para controle, workers para geração, objeto para blobs, cliente SPA com WS. Build order começa pelo **pipeline geométrico comprovado**, depois **contrato LLM**, depois **UI** e só então **orquestração tempo real** e **refino avançado**.

### Critical Pitfalls

1. **Schema frouxo** — evitar com validação estrita na Fase 2
2. **Blobs no relational** — MinIO desde a Fase 1
3. **Refino sem lint** — travar na Fase 5
4. **Seleção sem identidade estável** — mitigar na Fase 5 (documentar limites)

## Implications for Roadmap

| Phase | Rationale |
|-------|-----------|
| 1 | Sem geração confiável no backend, não há produto |
| 2 | Sem IntentSchema, escala de NL vira dívida semântica |
| 3 | Shell + viewer provam integração e picking futuro |
| 4 | WS completa a narrativa “copilot” |
| 5 | Diferenciação CAD (refino + diff + lint operacional) |

---
*Síntese para consumo do roadmap e do planejamento de fase.*
