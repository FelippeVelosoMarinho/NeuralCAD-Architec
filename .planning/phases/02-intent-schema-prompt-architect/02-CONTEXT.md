# Phase 2: Intent schema & Prompt Architect — Context

**Gathered:** 2026-05-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Esta fase entrega validação **`IntentSchemaV1`**, fluxo **NL → Claude (Prompt Architect)** com **intent estruturado válido ou clarificação**, derivação de **config interpretável pelo worker** (`generationConfig` alinhado a `IDEA.md`) e inclusão **mínima** de **trade-offs / risco geométrico previsto** antes ou na criação do job conforme INTENT-04.  
Não entrega shell UI, WebSockets nem BrepGen real — apenas contratos e orquestração backend coerentes com a Fase 1 (jobs, Celery, `payload_json`).
</domain>

<decisions>
## Implementation Decisions

### Compatibilidade com jobs pré-schema / INTENÇÃO INTENT-01

- **D-01:** Pedidos **`POST /api/v1/jobs`** que criam trabalho dirigido por intent devem passar por validação **`IntentSchemaV1` canónica** tal como em `IDEA.md` § *IntentSchemaV1*. Modelos Pydantic usam **`model_config extra="forbid"`** no tipo final entregue à persistência — sem campos fantasmas nos nós obrigatórios do MVP desta fase.
- **D-02:** O **shape canónico** no JSON gravado em `jobs.payload_json` segue **`IDEA.md`**: `intent`, **`constraints`** e restantes secções são **irmãos** ao mesmo nível (não aninhar só `constraints` dentro de `intent` como forma principal).
- **D-03:** Para não quebrar integrações já usadas na Fase 1, aceitar **`intent.constraints.dimensionsMm`** **apenas como entrada legado** durante a transição: normalizar antes de gravar (`constraints.dimensionsMm` + limpeza) e marcar campo opcional **`schemaVersion`** ou metadados internos se necessário para auditoria. O worker será actualizado para ler **primeiro** `payload_json["constraints"]["dimensionsMm"]` e **fallback** para o caminho legado até remoção explícita.
- **D-04:** Fluxo apenas “livre” sem passar Prompt Architect quando o texto NL estiver ausente pode continuar permitido apenas em **subset explícito** (ex.: testes) via rota ou flag documentada pelo planner — **fora deste MVP** usar defaults silenciosos em campos geométricos críticos.

### Política de clarificação (prompt ambíguo) — INTENT-02

- **D-05:** No caminho **`POST`** síncrono que envia **texto natural**, o backend responde **ou** `200` com **intent validado** (e metadados de risco), **ou** `409` / `422` (escolha final do planner) com corpo **estructurado** `clarification` contendo: `questions[]` (máx. **3** perguntas por ronda), `missingFields[]` opcional, `attempt` e **`maxAttempts: 2`** rondas por sessão de pedido (novo POST conta nova sessão).
- **D-06:** Após esgotar `maxAttempts` sem intent válido, devolver **`rejected`** com `reason` legível e **sem** criar job — nunca preencher `dimensionsMm` / espessuras com inventiva silenciosa.
- **D-07:** O Prompt Architect (Claude) deve devolver **JSON parseável** que mapeia para os modelos Pydantic; HTML ou prosa solta não são respostas finais de API.

### Ponte INTENT-03 — `generationConfig` e worker

- **D-08:** O bloco **`generationConfig`** (e `qualityTargets` quando relevante) do `IDEA.md` é **validado e persistido** em `payload_json` mesmo que o worker da Fase 2 **continue a usar geometria OCC de caixa**. O obrigatório aqui é **rastreabilidade**: o planner define como o worker consome subsets (modo, limites numéricos) sem exigir que BrepGen esteja disponível.
- **D-09:** Até ao motor BrepGen real, o worker **interpreta apenas** um subconjunto estável (`mode`, valores usados pelo stub) documentado pelo planner e **persiste ignorados** sob chave registada nos SUMMARY/tests para não perdê-los.

### Trade-offs e risco geométrico (INTENT-04)

- **D-10:** Cada fluxo bem-sucedido que produza intent validado antes de enqueue inclui objeto **`geo_risk`** com: `severity` (`info`|`warn`|`critical`), mensagens curtas previstas (ex.: risco auto-intersecção), e referência opcional a `qualityTargets`. **Enqueue não é bloqueado** por `warn`/`info`; **`critical`** pode bloquear criação de job **somente se** política definida pelo planner encontrar inconsistência objetiva entre intent numérico (ex.: dimensões impossíveis) — caso contrário `critical` só informativo na resposta até haver política forte.
- **D-11:** Gravar **snapshot** de `geo_risk` (e opcionalmente resumo textual) dentro de **`payload_json["preflight"]`** no momento da criação do job para alinhar D-06 da Fase 1 (reuso em regenerações / Fase futura Promp Architect sessão).

### Claude's Discretion

- Biblioteca cliente Anthropic (`anthropic` vs HTTPS directo), cache de prompts, modelo exacto Claude (Sonnet/Haiku) e timeouts — **livre desde** que INTENT-02/04 observados e custos/logs configuráveis por env.
- Formato exacto dos schemas Pydantic (nomes opcionais `Optional`) para campos do MVP — planner detalha tabela campo-a-campo com `IDEA.md`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Producto & contratos

- `IDEA.md` § *AI Orchestration Contract* — deveres 1–5 do Prompt Architect
- `IDEA.md` § *IntentSchemaV1 (Canonical)* — shape JSON obrigatório
- `.planning/REQUIREMENTS.md` — INTENT-01 … INTENT-04
- `.planning/ROADMAP.md` — Fase 2 goal e success criteria

### Fases anteriores & pipeline

- `.planning/phases/01-geometric-pipeline-platform/01-CONTEXT.md` — D-01…D-08 (alvo vs as-built, `dimensional_audit`, tolerâncias)
- `.planning/phases/01-geometric-pipeline-platform/01-VERIFICATION.md` — critérios FOUND já verificados
- `.planning/PROJECT.md` — stack e valores do produto

### Código de integração atual

- `services/api/src/neuralcad_api/main.py` — criação de job e enqueue Celery
- `services/api/src/neuralcad_api/schemas/jobs.py` — modelo actual `JobCreate` (a substituir/estender)
- `services/worker/src/neuralcad_worker/tasks/geometry.py` — leitura actual de dims (actualizar conforme D-03)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `services/api/` — FastAPI existente com `send_task("process_geometry_job", …)` já alinhado ao worker
- Worker `process_geometry_job` — ciclo OCC + MinIO + `dimensional_audit` reutilizado; só falta alinhar ingestão ao shape canónico

### Established Patterns

- Erros HTTP via `HTTPException`; persistência AsyncSession + modelo `Job` com JSONB
- Auditoria dimensional já gravada por job — estende-se com `preflight.geo_risk`

### Integration Points

- Novo fluxo Prompt Architect será chamado desde a camada de serviço **antes** de `Job` persistido + enqueue
- Futura UI (Fase 3+) consumirá o mesmo contrato de clarificação; manter payloads estáveis

</code_context>

<specifics>
## Specific Ideas

- Utilizador pediu explicitamente **`todas`** as áreas de discussão na sessão `/gsd-discuss-phase 2`; decisões acima consolidam **as opções recomendadas** pelo orquestrador em cada tema.
- Mantém foco combinado Phase 1: **mensurabilidade** entre intent numérico e OCC continua válida usando `constraints.dimensionsMm` canónico (`IDEA.md`).

</specifics>

<deferred>
## Deferred Ideas

### Reviewed Todos (not folded)

- Nenhuma todo casou esta fase via `todo.match-phase`.

**(Nenhuma ideia fora do âmbito — discussão ficou dentro do boundary da Fase 2.)**

</deferred>

---

*Phase: 02-intent-schema-prompt-architect*
*Context gathered: 2026-05-03*
