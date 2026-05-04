# Roadmap: NeuralCAD Architect

## Overview

Entrega incremental alinhada aos cinco sprints do brief: primeiro prova-se o **pipeline geométrico e infraestrutura**, em seguida o **contrato IntentSchema + Prompt Architect**, depois o **shell VS Code + viewport 3D**, o **loop tempo real**, e por fim **refino por seleção, lint e histórico/diff**. Cada fase mapeia requisitos disjuntos para permitir verificação clara.

## Phases

- [x] **Phase 1: Geometric pipeline & platform** - API, workers, armazenamento e primeira geração B-rep ponta a ponta no backend
- [ ] **Phase 2: Intent schema & Prompt Architect** - IntentSchemaV1, integração Claude, clarificações e config BrepGen
- [x] **Phase 3: VS Code-like UI & 3D foundation** - Layout shell, Monaco, viewport e explorer de topologia (`services/web/`).
- [ ] **Phase 4: Realtime orchestration** - WebSockets, progresso de jobs e fluxo completo pela UI *(PLANs drafted em `04-realtime-orchestration/`)*
- [ ] **Phase 5: Refinement, lint & iteration history** - Seleção, refinamento, lint geométrico, versões e diff visual

## Phase Details

### Phase 1: Geometric pipeline & platform
**Goal**: Backend capaz de enfileirar e completar jobs de geração B-rep, persistir artefatos e expor API mínima verificável.
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04
**Success Criteria** (what must be TRUE):
  1. Um cliente HTTP (script ou Swagger) pode criar um job e receber estado terminal de sucesso ou falha rastreável
  2. Artefato STEP e/ou STL gerado pode ser recuperado via API ou URL assinada/documentada
  3. Serviços definidos no `IDEA.md` sobem via Docker Compose sem passos manuais não documentados
**UI hint**: no
**Plans**: TBD (refinar em `/gsd-plan-phase 1`)

Plans:
- [x] 01-01: Repositório monorepo + Compose + serviços base
- [x] 01-02: Worker Celery + integração BrepGen mínima
- [x] 01-03: API de jobs + persistência Postgres/MinIO

### Phase 2: Intent schema & Prompt Architect
**Goal**: Todo fluxo de geração dirigido por intent passa por schema validado e camada LLM que produz IntentSchemaV1 ou clarificações.
**Depends on**: Phase 1
**Requirements**: INTENT-01, INTENT-02, INTENT-03, INTENT-04
**Success Criteria** (what must be TRUE):
  1. Payload inválido é rejeitado com erros de validação compreensíveis
  2. Prompt ambíguo retorna estrutura de clarificação em vez de silent defaults perigosos
  3. Intent válido resulta em tarefa de worker com parâmetros rastreáveis (auditoria mínima)
**UI hint**: no
**Plans**: TBD

Plans:
- [ ] 02-01: Modelos Pydantic IntentSchemaV1 + testes de contrato
- [ ] 02-02: Serviço Prompt Architect (Claude) + política de clarificação
- [ ] 02-03: Encadeamento API → intent → fila worker

### Phase 3: VS Code-like UI & 3D foundation
**Goal**: Shell de produto com Monaco, explorer de topologia e viewport capaz de exibir geometria gerada.
**Depends on**: Phase 2
**Requirements**: UI-01, UI-02, UI-03, UI-04
**Success Criteria** (what must be TRUE):
  1. Usuário percorre layout (sidebar, central, inferior) sem quebrar estado global
  2. Modelo servido pelo backend é visível no viewport com performance aceitável em asset de MVP
  3. Árvore reflete hierarquia esperada para o artefato de teste documentado
**UI hint**: yes
**Plans**: Ficheiros `.planning/phases/03-vs-code-like-ui-3d-foundation/03-{01..03}-PLAN.md`

Plans:
- [x] 03-01: App Vite + layout + estado global
- [x] 03-02: Integração Monaco + chamadas API
- [x] 03-03: Viewport Three/R3F + loader + explorer sincronizado

### Phase 4: Realtime orchestration
**Goal**: Experiência contínua da solicitação à conclusão com atualizações em tempo real.
**Depends on**: Phase 3
**Requirements**: RT-01, RT-02, RT-03
**Success Criteria** (what must be TRUE):
  1. Eventos de progresso de job chegam ao browser sem polling exclusivo
  2. Usuário completa fluxo feliz prompt→modelo na UI em ambiente de desenvolvimento
  3. Reconexão ou cancelamento não corrompe estado persistido no servidor
**UI hint**: yes
**Plans**: `.planning/phases/04-realtime-orchestration/04-{01..03}-PLAN.md` — ver `04-CONTEXT.md`

Plans:
- [ ] 04-01: Gateway WebSocket + autenticação de sessão
- [ ] 04-02: Mapeamento eventos worker → WS
- [ ] 04-03: TanStack Query + stores para consistência UI

### Phase 5: Refinement, lint & iteration history
**Goal**: Fechar diferenciais CAD: refino guiado, qualidade visível e comparativo entre iterações.
**Depends on**: Phase 4
**Requirements**: REFINE-01, REFINE-02, QUAL-01, QUAL-02
**Success Criteria** (what must be TRUE):
  1. Seleção de entidade dispara fluxo de refinamento com resultado mensurável no B-rep
  2. Lint geométrico aparece no painel copiloto com severidade compreensível
  3. Usuário alterna entre duas versões e vê destaque de mudança (metodo MVP documentado)
**UI hint**: yes
**Plans**: TBD

Plans:
- [ ] 05-01: Picking + modelo de seleção estável o suficiente para MVP
- [ ] 05-02: Pipeline refinamento + integração OCC lint
- [ ] 05-03: Versionamento + UI diff

## Progress

**Execution Order:** Phases 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Geometric pipeline & platform | 3/3 | Complete | 2026-05-03 |
| 2. Intent schema & Prompt Architect | 0/TBD | Not started | - |
| 3. VS Code-like UI & 3D foundation | 3/3 | Complete | 2026-05-03 |
| 4. Realtime orchestration | 0/3 | In progress — PLANs drafted 2026-05-03 | — |
| 5. Refinement, lint & iteration history | 0/TBD | Not started | - |
