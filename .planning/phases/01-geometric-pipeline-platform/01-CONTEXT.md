# Phase 1: Geometric pipeline & platform - Context

**Gathered:** 2026-05-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Esta fase entrega backend com fila de jobs, workers, Postgres + MinIO, Docker Compose e **primeira geração B-rep ponta a ponta** com API mínima verificável (FOUND-01..04). A discussão **não expande** o roadmap: clarifica **como** embutir, já no protótipo, a integração entre **valores dimensionais do IntentSchemaV1** (entrada preparada para Claude na Fase 2) e **medições reais via pythonocc** no sólido gerado, para estabelecer **fidelidade dimensional auditável** desde o primeiro pipeline.

</domain>

<decisions>
## Implementation Decisions

### Ponte IntentSchema (alvo) ↔ pythonocc (as-built)

- **D-01:** Campos numéricos relevantes do IntentSchemaV1 — em especial `constraints.dimensionsMm` (width / height / depth) e `constraints.thicknessMm` — são tratados como **intenção declarativa (target)** quando presentes no payload do job. Valores derivados do B-rep final via **pythonocc-core** são a fonte **as-built** no protótipo.
- **D-02:** Após a geração e **antes** de marcar o job como sucesso, o worker executa um passo obrigatório de **medição OCC**: carregar o resultado (priorizar TOPO sólido igual ao exportado para STEP), calcular **bounding box** mundial (ex.: `BRepBndLib` + `Bnd_Box`), e registrar **extents em mm** ao longo de **X, Y e Z** como `bbox_mm: { width, height, depth }` com convenção de eixo documentada no código (ordenar ou rotular de forma estável para comparar com `dimensionsMm`).
- **D-03:** Persistir no Postgres (JSONB no registro de artefato/versão de job) um objeto **`dimensional_audit`**: `target` (subconjunto espelhado do intent, ou `null` se fluxo apenas unconditional), `measured` (bbox + `source: "pythonocc"`, timestamp, versão do worker), `delta` (diferenças por eixo em mm e percentual opcional) e `withinTolerance` quando `target` existir. Sem intent numérico, popular apenas `measured` — atende FOUND sem exigir Fase 2 completa.
- **D-04:** **Tolerância do protótipo:** considerar aderência **OK** se, por eixo, `|measured - target| <= max(0.5 mm, 1% * target)` quando target > 0; se target for 0 ou ausente, não calcular `withinTolerance`. Desvios **não falham** o job na Fase 1: retornam **report** (`severity`, eixos fora) para métricas e para a Fase 2/UI.
- **D-05:** **Espessura (`thicknessMm`):** no protótipo, **opcional** — se não houver rotina OCC estável a tempo, registrar `thickness_mm: null` no audit com razão (`not_implemented`); se implementável como estimativa simples (ex. amostragem em shell), preencher número único e documentar limitação.
- **D-06:** Contrato HTTP interno: endpoint de detalhe do job / artefato expõe `dimensional_audit` para scripts e, na Fase 2, para o Prompt Architect reutilizar em regeneração (campo reservado na sessão — não exigido fechar na Fase 1, mas schema de resposta **compatível**).

### Infra e ordem do pipeline

- **D-07:** A medição OCC corre no **mesmo worker** que gera/pós-processa o STEP, imediatamente após escrita no MinIO e antes do commit transacional do status `success`.
- **D-08:** Imagem Docker do worker inclui **pythonocc-core** e deps de sistema necessárias; builds reprodutíveis documentados (sem “funciona na minha máquina”).

### Claude’s Discretion

- Detalhe da API exata do endpoint (nome de campos, paginação) e biblioteca auxiliar OCC para leitura STEP — **a cargo do planner**, respeitando D-01–D-08.
- Estratégia exata de mapeamento eixo-a-eixo se `dimensionsMm` usar convenção diferente do bbox OCC — implementação pode escolher rotação mínima ou ordenar extents; deve ser **documentada e testada** com um caso referência.

</decisions>

<specifics>
## Specific Ideas

**Foco explícito do utilizador** (`--context`): concentrar-se na integração entre o **IntentSchema (saída estruturada do Claude, Fase 2)** e a **extração de medidas reais via pythonocc**, garantindo **fidelidade dimensional mensurável** já no primeiro protótipo — isto inclui auditoria persistida e deltas, não apenas bbox “para debug”.

Referência de forma de dados: `IDEA.md` § IntentSchemaV1 (`constraints.dimensionsMm`, `thicknessMm`).

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/ROADMAP.md` — Phase 1 goal, success criteria, requirements FOUND-01..04
- `.planning/REQUIREMENTS.md` — FOUND-* e traceability
- `.planning/PROJECT.md` — stack fechada, contrato IntentSchema, core value

### Product contract

- `IDEA.md` — IntentSchemaV1 canônico, workflows MVP, riscos (ambiguidade, sólidos inválidos)

### Research (opcional contexto)

- `.planning/research/ARCHITECTURE.md` — fluxo API → fila → worker → storage
- `.planning/research/PITFALLS.md` — armadilhas de topologia e ambiguidade

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- Nenhum — repositório ainda sem código de aplicação; primeira implementação nesta fase.

### Established Patterns

- Não aplicável; seguir `.planning/PROJECT.md` e `IDEA.md` para stack.

### Integration Points

- API FastAPI (criação/consulta de jobs), worker Celery, Postgres (JSONB `dimensional_audit`), MinIO (STEP/STL), futura ligação Fase 2 ao Prompt Architect via mesmo contrato de audit.

</code_context>

<deferred>
## Deferred Ideas

- Validação completa IntentSchemaV1 + clarificações Claude (**Fase 2**).
- Lint geométrico alargado (watertight, interseções) como gate duro (**Fase 5** / pesquisa).
- PMI ou GD&T rico — fora do protótipo de bbox/audit.

### Reviewed Todos (not folded)

- Nenhum (`todo.match-phase` retornou lista vazia).

</deferred>

---

*Phase: 01-geometric-pipeline-platform*
*Context gathered: 2026-05-03*
