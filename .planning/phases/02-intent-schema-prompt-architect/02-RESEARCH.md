# Phase 2 — Technical research (Intent schema & Prompt Architect)

**Date:** 2026-05-03

## Questions answered

- Como validar **`IntentSchemaV1`** de forma estrita em Python mantendo alinhamento com `IDEA.md`?
- Como integrar **Claude** como Prompt Architect com JSON estruturável e erros tratáveis?
- Como separar **elicitação NL** (com clarificação) de **criação de job** determinística?
- Como o **worker** deve ler `constraints.dimensionsMm` canónico sem quebrar payloads legados?

## Findings

### Pydantic / INTENT-01

- **Pydantic v2** (`model_config = ConfigDict(extra="forbid")`) no modelo raiz e sub-modelos críticos garante rejeição de campos desconhecidos sem ambiguidade.
- O JSON canónico em `IDEA.md` mistura chaves com valores `0` e listas vazias como exemplos — distinguir **valor de exemplo** de **default de produção**: usar `Optional`/defaults explícitos apenas onde o CONTEXT marca MVP; campos numéricos geométricos não devem inventar defaults perigosos quando ausentes (validação falha ou clarificação upstream).
- Gerar **fixture JSON** mínimo nos testes que espelha literalmente a forma de `IDEA.md` § IntentSchemaV1.

### Anthropic / INTENT-02

- SDK oficial **`anthropic`** com `Anthropic.messages.create`, modelo configurável (`ANTHROPIC_MODEL`, default Sonnet classe), timeout e `max_tokens`.
- Para **JSON parseável**: instruções de sistema rígidas + pedido de resposta apenas em fenced `json` **ou** output JSON único sem prosa; pós-processar removendo markdown se necessário.
- **Testes CI:** mockar cliente com `unittest.mock` ou `pytest-httpx` — nunca chamada rede real obrigatória em `pytest`.

### Rotas HTTP

- **`POST /api/v1/intent/elicit`** (nome final executor pode harmonizar mas manter prefixo `/api/v1`): corpo `{ "prompt": "<NL>", "attempt": <int opcional default 1> }`. Devolve ou `IntentSchemaV1` + `geo_risk` + `preflight` ou corpo **`422`** com `detail` discriminado `{ "type": "clarification_needed", ... }` alinhado a `02-CONTEXT.md` D-05.
- **`POST /api/v1/jobs`** passa a aceitar apenas **`IntentJobRequest`** (nome interno): wrapper com campos obrigatórios do intent canónico + opcional cópia de `preflight` validada pelo schema local — remove `extra=allow` do MVP de produção.
- Fluxo opcional documentado no README: `elicit` → copiar JSON → `POST /jobs` (ou cliente único que encadeia internamente).

### Worker / INTENT-03

- Função única **`resolve_dimensions_target(payload: dict)`** em `geometry.py` (ou módulo `payload_compat.py`): ordem de leitura `payload["constraints"]["dimensionsMm"]` → fallback `payload.get("intent",{}).get("constraints",{}).get("dimensionsMm")`.
- `generationConfig` e `qualityTargets` lidos e **registados** em logs ou campo debug até BrepGen — não alterar geometria OCC na Fase 2 além do subset documentado no plano.

### Risco geométrico / INTENT-04

- Modelo Pydantic **`GeoRisk`** com `severity: Literal["info","warn","critical"]`, `messages: list[str]`, opcional `quality_ref`.
- Heurística local adicional (sem LLM) para **dimensões não positivas** → `critical` + bloqueio opcional conforme plano (política explícita no código).
- Persistência: `payload_json["preflight"] = {"geo_risk": ..., "schema_version": "1" }` na criação do job.

## Validation Architecture

| Dimension | Strategy |
|-----------|----------|
| Schema contract | `pytest` em `services/api/tests/` com casos positivos/negativos `extra=forbid` |
| LLM boundary | Testes com mock do cliente Anthropic; contrato de parse JSON |
| HTTP | `httpx.AsyncClient` contra app FastAPI em testes de integração leves (lifespan real, DB mock ou sqlite opcional — preferir Postgres testcontainer só se já existir; senão mock session) |
| Worker compat | Teste unitário de `resolve_dimensions_target` com dicts canónico + legado |

**Automated quick command (per task):** `cd services/api && python -m pytest -q --tb=short tests/test_intent_schema.py` (expandir globs conforme ficheiros existirem).

**Full suite (wave end):** `cd services/api && python -m pytest -q --tb=short`

## Dependencies to add

- `anthropic>=0.40` (ajustar versão no lock ao implementar)
- `pytest`, `httpx` em optional-dev (já referência em Fase 1 `pyproject` optional)

## Open items (Claude's discretion)

- Nome exacto final dos paths OpenAPI; split router em `routers/intent.py` vs tudo em `main.py`.
- Versão exacta do modelo Claude e limites `max_tokens`.

---

## RESEARCH COMPLETE
