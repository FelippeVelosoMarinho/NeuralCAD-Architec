# Requirements: NeuralCAD Architect

**Defined:** 2026-05-03
**Core Value:** Descrever intenção em NL e obter B-rep válido com rastreabilidade, qualidade visível e refinamento iterativo — sem depender de operador CAD para cada passo.

## v1 Requirements

### Foundation — backend & infrastructure

- [ ] **FOUND-01**: Operador pode subir ambiente local via Docker Compose com API, worker, Redis, Postgres e MinIO disponíveis
- [ ] **FOUND-02**: Sistema pode enfileirar job de geração geométrica e processá-lo em worker Celery
- [ ] **FOUND-03**: Cliente HTTP pode solicitar geração “incondicional” (sem IntentSchema completo na v1 desta fase, conforme plano da fase) e receber identificador de job e estado
- [ ] **FOUND-04**: Artefato gerado (STEP e/ou STL) pode ser persistido em armazenamento de objetos e referenciado por metadados em Postgres

### Intent & AI orchestration

- [ ] **INTENT-01**: Sistema pode validar payload contra modelo Pydantic equivalente a **IntentSchemaV1**
- [ ] **INTENT-02**: Usuário pode enviar texto natural ao backend e receber **IntentSchemaV1** validado ou uma resposta estruturada de clarificação mínima
- [ ] **INTENT-03**: Sistema pode derivar configuração BrepGen-a partir de intent validado e repassá-la ao worker
- [ ] **INTENT-04**: Antes da geração, resposta ao cliente pode incluir trade-offs e riscos geométricos previstos (campos definidos na implementação)

### UI shell & 3D

- [ ] **UI-01**: Usuário pode ver layout estilo VS Code com barra lateral, área central e painel inferior
- [ ] **UI-02**: Usuário pode editar prompt em Monaco na área central
- [ ] **UI-03**: Usuário pode visualizar geometria no viewport Three.js (carregamento a partir de artefato servido pela API)
- [ ] **UI-04**: Usuário pode explorar hierarquia B-rep (faces/arestas/vértices) na barra lateral alinhada ao modelo carregado

### Realtime orchestration

- [ ] **RT-01**: Cliente pode manter canal WebSocket autenticado/sessão com backend para eventos de job
- [ ] **RT-02**: Usuário pode enviar fluxo prompt→geração pela UI e observar progresso até modelo disponível no viewport
- [ ] **RT-03**: Estado exibido na UI permanece coerente com servidor (TanStack Query + contratos de estado documentados)

### Refinement, quality & history

- [ ] **REFINE-01**: Usuário pode selecionar entidades (face/edge/vertex) na árvore ou viewport para contexto de refinamento
- [ ] **REFINE-02**: Sistema pode aplicar caminho de refinamento (interpolação/autocompletion conforme desenho da fase) e retornar nova versão
- [ ] **QUAL-01**: Usuário pode ver resultados de lint geométrico (p.ex. watertight, risco de auto-interseção) no painel copiloto
- [ ] **QUAL-02**: Usuário pode navegar entre iterações anteriores e ver indicadores de diff visual entre versões

## v2 Requirements

### Collaboration & scale

- **V2-COLLAB-01**: Múltiplos usuários podem colaborar em tempo real no mesmo projeto
- **V2-COLLAB-02**: Presença e cursores podem ser exibidos na UI

### CAD depth

- **V2-CAD-01**: Montagem multi-corpo com constraints de alto nível (paridade aproximada a CAD enterprise)
- **V2-CAD-02**: Bibliotecas de peças padrão integradas

### Auth & enterprise

- **V2-AUTH-01**: SSO corporativo (SAML/OIDC)
- **V2-AUTH-02**: RBAC e workspaces organizacionais

## Out of Scope

| Feature | Reason |
|---------|--------|
| Suíte CAD completa | MVP = co-piloto de conceito/refino, não substituição Swap total |
| Paridade montagem enterprise na v1 | Complexidade; explicitamente “Non-Goals” do brief |
| Colaboração multi-usuário realtime na v1 | Infra OT; adiado a v2 |
| Retreino BrepGen na primeira release | Depende de dados e pesquisa; fora do MVP |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Pending |
| FOUND-02 | Phase 1 | Pending |
| FOUND-03 | Phase 1 | Pending |
| FOUND-04 | Phase 1 | Pending |
| INTENT-01 | Phase 2 | Pending |
| INTENT-02 | Phase 2 | Pending |
| INTENT-03 | Phase 2 | Pending |
| INTENT-04 | Phase 2 | Pending |
| UI-01 | Phase 3 | Pending |
| UI-02 | Phase 3 | Pending |
| UI-03 | Phase 3 | Pending |
| UI-04 | Phase 3 | Pending |
| RT-01 | Phase 4 | Pending |
| RT-02 | Phase 4 | Pending |
| RT-03 | Phase 4 | Pending |
| REFINE-01 | Phase 5 | Pending |
| REFINE-02 | Phase 5 | Pending |
| QUAL-01 | Phase 5 | Pending |
| QUAL-02 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-03*
*Last updated: 2026-05-03 after roadmap creation*
