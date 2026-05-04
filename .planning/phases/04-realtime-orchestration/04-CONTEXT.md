---
phase: 04-realtime-orchestration
slug: realtime-orchestration
status: context-sealed
gathered: 2026-05-03
depends_on_phase: "03-vs-code-like-ui-3d-foundation"
---

# Phase 4: Realtime orchestration — Context

**Gathered:** 2026-05-03  
**Status:** Ready for planning / execution (**decisões fechadas abaixo**)

---

<domain>

## Phase Boundary

Entregar canal **tempo real** (WebSocket + Redis Pub/Sub) para progresso de **jobs** até geometria disponível; **eliminar polling activo** na UI substituindo por eventos multicasted; incluir **cancelamento acionável** no MVP; expor granulosidade de pipeline alinhada a **etapas de engenharia** nomeadas até **BrepGen / OCC** cobrir cada fase.

Fora da fase: colaboração multi‑utilizador além do **multicast ao mesmo job_id**, streaming binário STEP/STL pelo WS, auth enterprise.

---

<decisions>

## Implementation Decisions

### Cancelamento (_área 1_)

- **D-04-01:** **Cancelamento MVP acionável** via **`DELETE /api/v1/jobs/{id}`** (sem corpo obrigatório).
- **D-04-02:** Ao cancelar com sucesso: marcar estado persistido (**`status`** terminal **`cancelled`** ou equivalente documentado); **revogar tarefa Celery** quando ainda aplicável (**`task_id`** guardado no job no `POST /jobs`).
- **D-04-03:** Broadcast **`job.cancelled`** (tipo canónico Redis/WS — ver contrato plano **04‑02**) a todas as subscrições do `job_id`.
- **D-04-04:** **`DELETE`** em job já **`success`** / **`failed`** / **`cancelled`** → responder **409** ou **410** conforme política definida na implementação (**Claude discretion**: preferir **409**).
- **D-04-05:** Worker verifica periodicamente **flag de cancelamento** entre estágios de pipeline (**Claude discretion**: coluna Postgres ou só revocação Celery conforme menor fricção; sem alterar comportamento bem‑sucedido de jobs completos).

### Granularidade de progresso (_área 2_)

- **D-04-06:** **`job.pipeline_stage`** obrigatório no contrato de eventos onde `type === "job.progress"` (**ou campo homólogo** no `detail`): enum **fixo MVP** seguindo a ordem lógica de engenharia:
  **`PROMPTING`**, **`DENOISING_FACES`**, **`DENOISING_EDGES`**, **`SEWING`**, **`MEASURING_ABNT`**  
  até evolução do motor BrepGen; nomes são **contrato API** estável.
- **D-04-07:** Stub actual (`build_box_shape` + STEP/STL + medida) deve **emitir todos os valores do enum ao longo do processamento**, ancorados a pontos reais no código (**mapeamento inicial** até pipeline rico subsistuir):
  - **PROMPTING** — após job transitar para **`running`** (post‑enqueue).
  - **DENOISING_FACES** — imediatamente antes de **`build_box_shape`** (substituível quando existir verdadeira reparação de faces).
  - **DENOISING_EDGES** — após geometria sintética válida antes de **`shape_to_step_bytes`** (placeholder semântico “arestas saneadas”).
  - **SEWING** — antes/durante escrita STEP + STL (**carcaça sólida fechada**).
  - **MEASURING_ABNT** — após **`measure_bbox_mm`** / construção de **`dimensional_audit`** (métricas + tolerância).
- **D-04-08:** Todas as transições de estado **`pending`/`running`/`success`/`failed`/`cancelled`** também emitem **`job.lifecycle`** (**Claude discretion** no campo exacto desde que documentado no SUMMARY dos PLANs).

### Multi‑client (_área 5_)

- **D-04-09:** **Multicast garantido pelo Redis Pub/Sub** canal único **`neuralcad:job:{job_id}`**: qualquer cliente WS subscreve o mesmo namespace; atualizações partilham **fluxos 2D/3D em simultâneo** quando duas vistas consomem o mesmo `jobId`.
- **D-04-10:** Servidor não distingue “aba” nem “painel”: responsabilidade de **UI** garantir dois painéis com o mesmo `jobId`; backend só **replay** inicial não é obrigatório no MVP (**Claude discretion**: opcional último estado via GET após reopen).

### Sessão e auditoria (`client_session`) — defaults _área 3_

- **D-04-11:** **`client_session` query parameter obrigatório** em **`GET` upgrade WebSocket** (UUID v4). Sem ele → **`4401`** (**Claude discretion** código WebSocket próximo ao meaning “policy violation”) ou fechar conn com razão textual.
- **D-04-12:** Persistência mínima: log estrut opcional só em dev; obrigatório é **ecoar `client_session`** no evento inicial **`subscribed`** para depuração do cliente (**Claude discretion**).

### UI e redes de segurança — defaults _área 4_

- **D-04-13:** **Sem polling (`setInterval` GET) durante operação nominal** na UI **`useJobFlow`**.
- **D-04-14:** **Um único `GET /api/v1/jobs/{id}`** apenas em **fall back de erro de rede WS / após falha reconnect** antes de novo WS (**re‑sync**) ou ao mount se necessário primeiro snapshot antes do WS estar pronto (**Claude discretion**: ordem `POST job` → snapshot GET → WS é aceite).

### Claude's Discretion

- Código numérico exacto WS para recusas; forma de **`revoke` Celery + persistência `celery_task_id`**; formato exacto campo `detail` **desde que** documentado nos SUMMARY **04‑01 … 03** e invariantes **Redis** preservados (**schemaVersion `"1"`** mantido até bump explícito).

---

<specifics>

## Specific Ideas

- Feedback de progresso dirigido a **engenheiros**: copy / UI pode mostrar rótulos de **etapa** lado a lado com vistas 3D quando existIREM (fora âmbito copy nesta decisão técnica).
- Paralelo **CAD 2D/3D futuro**: multicast ao mesmo **`job_id`** é requisito intencional pelo utilizador para experiências duplicadas cliente.

---

<canonical_refs>

## Canonical References

**Downstream agents MUST read:**

- `.planning/ROADMAP.md` — Phase 4 goals RT‑01 … RT‑03
- `.planning/REQUIREMENTS.md` — RT‑01, RT‑02, RT‑03
- `.planning/research/ARCHITECTURE.md` — WebSocket gateway
- `.planning/phases/04-realtime-orchestration/04-{01,02,03}-PLAN.md` — PLANs executables (subject to refresh after CONTEXT seal)
- `services/api/src/neuralcad_api/main.py` — inclusão routers + `send_task`

---

<code_context>

## Existing Code Insights

### Reusable Assets

- **Celery** `celery_app.send_task("process_geometry_job", …)` sem persistir `task_id` — **mudança obrigatória** para revoke (**D‑04‑02**).
- **Redis broker** já partilhado por API/worker Compose.
- **`useJobFlow`** usa polling — substituído pela Fase **04‑03**.
- **`Job`** modelo SQLAlchemy só `status`, sem `cancelled`.

### Established Patterns

- JSONB `payload_json`, `dimensional_audit`.
- Artefactos **`jobs/{id}/model.step|stl`**.

### Integration Points

- Novo **`ws` pacote**, **`DELETE`** router sobre `jobs`, worker **`realtime.publish`**, storefront hooks.

---

<deferred>

## Deferred Ideas

- **Realtime colaborativo** multi‑job / presença (V2).
- **SSE** paralelo aos WS (**só WS** MVP).
- **Replay** servidor de backlog de todos eventos só para novo subscriber (**fora MVP**).

---

_Phase: 04-realtime-orchestration · Context sealed: 2026-05-03_
