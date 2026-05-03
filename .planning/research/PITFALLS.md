# Pitfalls Research

**Domain:** Generative B-rep + LLM orchestration
**Researched:** 2026-05-03
**Confidence:** HIGH (riscos espelhados do `IDEA.md` e práticas comuns)

## Critical Pitfalls

### Pitfall 1: Ambiguidade de prompt sem trava de schema

**What goes wrong:** LLM “preenche buracos” com suposições erradas → geometria válida mas errada para o usuário.

**Why it happens:** Cad pipelines toleram pouca incerteza dimensional/topológica.

**How to avoid:** IntentSchemaV1 obrigatório; campos obrigatórios e perguntas mínimas; rejeitar geração sem domínio validado.

**Warning signs:** Alta taxa de regeneração; comentários “não era isso” sem erros de lint.

**Phase to address:** Phase 2 (Intent / Prompt Architect)

---

### Pitfall 2: Sólidos inválidos ou frágeis após refinamento local

**What goes wrong:** Edição local quebra manifold ou introduz auto-interseções.

**Why it happens:** Operações locais sem cheque de conectividade global.

**How to avoid:** Lint antes de “commitar” iteração; rollback para versão anterior; reparo conservador documentado.

**Warning signs:** Falhas intermitentes no export STEP; divergência viewer vs kernel.

**Phase to address:** Phase 5 (Refinement + quality)

---

### Pitfall 3: Acoplamento blob DB

**What goes wrong:** Performance ruim, backups caros, migrações difíceis.

**Why it happens:** STEP/STL são grandes demais para linha de tabela.

**How to avoid:** MinIO desde o dia 1; Postgres só metadados e ponteiros.

**Warning signs:** Queries lentas; tamanho de DB explodindo.

**Phase to address:** Phase 1 (Foundation / API)

---

### Pitfall 4: Latência percebida sem UX de fila

**What goes wrong:** Usuário clica “gerar” e assume travamento.

**Why it happens:** Inferência + OCC podem levar dezenas de segundos a minutos.

**How to avoid:** Jobs assíncronos + progresso WS + preview rápido quando possível.

**Warning signs:** Timeouts HTTP; duplo submit; abandono na primeira demo.

**Phase to address:** Phase 4 (Realtime orchestration)

---

### Pitfall 5: IDs de topologia instáveis entre versões

**What goes wrong:** Seleção “face 12” deixa de corresponder após regeneração.

**Why it happens:** Rebuild de B-rep pode renumerar entidades.

**How to avoid:** Mapeamento semântico (features) ou hashing geométrico; documentar limites do MVP.

**Warning signs:** Refino por seleção aleatório ou silenciosamente errado.

**Phase to address:** Phase 5 (Refinement)

---

*Mapeamento de fases alinhado ao ROADMAP deste projeto.*
