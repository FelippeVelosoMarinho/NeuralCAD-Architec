# Phase 2: Intent schema & Prompt Architect — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-05-03
**Phase:** 02-intent-schema-prompt-architect
**Areas discussed:** Compatibilidade pré-schema • Clarificação • Ponte worker/BrepGen config • Trade-offs / risco geométrico

**Modo:** O utilizador respondeu **`todas`** à selecção inicial de áreas cinzentas; para cada tema aplicaram-se **as recomendações** já expostas no passo `present_gray_areas` (equiv. a seleccionar a linha recomendada em cada decisão binária/ternária implícita).

---

## 1 — Compatibilidade com jobs “pré-schema”

| Option | Description | Selected |
|--------|-------------|----------|
| A | Validação estrita IntentSchema no `POST` + quebra legado sem caminho alternativo | |
| B | Validação estrita no payload persistido + **normalização única** de legado (`intent.constraints` → `constraints` IDEA) antes de gravar | ✓ |
| C | Manter dois endpoints paralelos indefinite | |

**User's choice:** B (alinha INTENT-01 e reduz dois contratos permanentes.)

**Notes:** Legado apenas como entrada transitória; canónico = `IDEA.md`.

---

## 2 — Política de clarificação

| Option | Description | Selected |
|--------|-------------|----------|
| A | Resposta sempre estruturada; máx **2** rondas; sem defaults silenciosos em geometria sensível | ✓ |
| B | Mais rondas com wizard longo | |
| C | Texto livre sem schema de clarificação | |

**User's choice:** A

**Notes:** Após falha repetida → `rejected`, sem criar job.

---

## 3 — Ponte INTENT-03 (generationConfig ↔ worker stub)

| Option | Description | Selected |
|--------|-------------|----------|
| A | Validar/persistir `generationConfig`; worker stub ignora até BrepGen; rastreio completo | ✓ |
| B | Omitir generationConfig até fase futura | |
| C | Simular sempre um único default sem persistir | |

**User's choice:** A

**Notes:** Obrigatoriedade é rastreabilidade e contrato validado.

---

## 4 — INTENT-04 (trade-offs / risco)

| Option | Description | Selected |
|--------|-------------|----------|
| A | `geo_risk` na resposta + snapshot `preflight`; warn/info não bloqueiam enqueue | ✓ |
| B | Bloqueio agressivo em qualquer alerta LLM | |
| C | Só texto na response HTTP sem persistência | |

**User's choice:** A

**Notes:** `critical` só bloqueia se inconsistência factual validável (opcional política forte).

---

## Claude's Discretion

Implementação cliente Anthropic, modelo, timeouts, granularidade opcional nos modelos Pydantic — decididas em plan/execução dentro dos limites D-05–D-11.

## Deferred Ideas

(Nenhuma fora da fase nesta sessão.)
