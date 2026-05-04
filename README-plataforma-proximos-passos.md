# Próximos passos da plataforma — BrepGen, UI (`ui_prototypes`) e Phase 5 (GSD)

Guia mestre para o que falta fechar produto segundo `IDEA.md`, `.planning/ROADMAP.md` e requisitos `REFINE-*` / `QUAL-*`.

---

## 1. Onde estamos vs o que falta

| Área | Estado resumido | Notas |
|------|-----------------|-------|
| **Infra Compose + jobs + OCC stub** | Operacional na prática no repo | Worker ainda só **caixa** OCC em `stub_solid.py` |
| **IntentSchema + Prompt Architect** | Grande parte já existe (`/intent/elicit`, normalização LLM); ver tracking em ROADMAP fase 2 | **INTENT-03** (derivar config BrepGen e passar ao worker) **não está feito** até integrar motor |
| **UI shell + viewport + realtime** | Fases 3–4 concluídas no roadmap implementado | Alinhar futuro look com **`ui_prototypes/*.png`** (ver §4) |
| **BrepGen** | Planeado (`IDEA.md`); código **ausente** | Repositório: [`samxuxiang/BrepGen`](https://github.com/samxuxiang/BrepGen) |
| **Phase 5** | Planos só no ROADMAP (05-01 … 05-03); **Plans: TBD** em detalhe | Picking/refino, lint, histórico/diff |

O ficheiro `ui_prototypes/` no raiz existe para receber mocks — ver `ui_prototypes/README.md`.

---

## 2. Integração com BrepGen (passo a passo técnico)

Objetivo: o worker Celery gerar STEP/STL a partir dos checkpoints oficiais, mantendo Postgres/MinIO/audit existentes.

### 2.1 Pré-requisitos fora deste mono-repo

1. Clone [`samxuxiang/BrepGen`](https://github.com/samxuxiang/BrepGen) e segue o **README** (Python **3.9**, PyTorch **2.2**, CUDA **11.8**, Diffusers **0.27**, OCC/ocwl conforme projeto).
2. Descarrega **checkpoints pré-treinados** da secção *Pretrained Checkpoint* do README (**Google Drive**: VAE + latent diffusion por dataset **DeepCAD** ou **ABC**).
3. Ajusta `eval_config.yaml` / caminhos apontados em `sample.py` para a pasta onde descompactaste os pesos.

### 2.2 Prova isolada (“fora da NeuralCAD”)

```bash
# Dentro do env BrepGen, com paths corrigidos:
python sample.py --mode abc
```

Confirma que gera STEP/STL no disco segundo o projeto.

### 2.3 Encaixe na NeuralCAD (`services/worker`)

1. **`GEOMETRY_ENGINE` (env)**  
   Sugestão: `occ_stub | brepgen` — quando `brepgen`, usar runner dedicado.

2. **Nova camada** (exemplo de layout de módulos)  
   - `neuralcad_worker/geometry/brepgen_runner.py` — inicializa modelo; recebe tensores/semente/config; devolve **`TopoDS_Shape`** ou bytes STEP; ou faz wrap do `sample.py` visto como subprocess (MVP rápido, menos bonito).

3. **Mapeamento Intent → BrepGen** (INTENT-03)  
   - Ler `payload_json` do job já persistido (`IntentSchema` + opcional **`generationConfig`** do `IDEA.md`).  
   - Implementar uma função `intent_to_brepgen_config(payload: dict) -> dict` que preencha o que o projeto BrepGen espera na inferência condicionada — se o paper só faz geração *não condicionada*, documentar limitação até evolução própria.

4. **`process_geometry_job` (`tasks/geometry.py`)**  
   - Ramificar: se `brepgen` → `runner.run(...)`.  
   - Reutilizar `shape_to_step_bytes`, `shape_to_stl_bytes`, `measure_bbox_mm`, uploads MinIO — ou, se só receberes STEP ficheiro, caminho intermediário OCC load.

5. **Docker**  
   - Imagem atual do worker (**Miniconda + pythonocc só**) não inclui CUDA/PyTorch.  
   - Opções: imagem **`nvidia/cuda`** + instalar conda env BrepGen; ou **serviço GPU lateral** só inferência chamado por HTTP pelo worker.

6. **Operacional**  
   - Timeouts Celery grandes; progresso já tem Redis — alinhar nomes das etapas com durações reais.  
   - Fallback: mantém OCC stub quando `GEOMETRY_ENGINE=occ_stub`.

7. **Testes**  
   - Unitários mocked na fronteira; um teste de integração marcado opcional/`@pytest.mark.gpu`.

---

## 3. Reforma da interface baseada nos PNG (`ui_prototypes/`)

Os ficheiros ainda são **opcionais** — coloca aqui exports Figma/Stitch/sketch.

### 3.1 Preparação de design

1. Coloca todas as vistas em **`ui_prototypes/`** (nomes descritivos; ver `ui_prototypes/README.md`).
2. Marca sobre cada PNG **tokens**: cores, espaçamentos, hierarquia (sidebar vs copilot vs viewport).
3. (Opcional) Extrai texto de marcação por componente ↔ ficheiros atuais em `services/web/src/components/`.

### 3.2 Implementação gradual (para não regressar realtime)

Ordem recomendável:

| Onda | Foco | Ficheiros típicos |
|------|------|-------------------|
| A | Tokens CSS (`global.css`), tipografia | `services/web/src/styles/` |
| B | Shell (`AppShell`, toolbar, splitter) sem lógica 3D | `components/layout/` |
| C | Monaco + painel inferior conforme PNG | `PromptEditor`, `App.tsx` hooks |
| D | Copilot / lint placeholders alinhados a Phase 5 | painel inferior vazio bem estilizado |
| E | Explorer + viewport apenas após lint/picking decididos na Phase 5 | `TopologyExplorer`, `MeshViewport` |

Critérios: **TanStack Query + WS intactos**, `VITE_API_BASE_URL` inalterável.

### 3.3 Se usares Stitch / ferramentas de geração

1. Prompt com referência **“match layout of attached PNG folder ui_prototypes/”**.
2. Revisão humana no browser (responsividade, dark theme).
3. Fundir código gerado aos hooks existentes (`useJobFlow`, `useMeshFromJob`), não substituir cegamente.

---

## 4. Restante execução **Phase 5** com **GSD** (Get Shit Done)

A Phase 5 no `.planning/ROADMAP.md` fecha **REFINE-01/02**, **QUAL-01/02** via três pacotes formais quando existirem `PLAN.md`:

- **05-01**: Picking + modelo de seleção MVP  
- **05-02**: Pipeline refinamento + OCC lint  
- **05-03**: Versionamento + UI diff  

Hoje aparece **`Plans: TBD`** na secção de detalhes — tens de materializar PLANs antes do `/gsd-execute-phase`.

### 4.1 Sequência GSD típica (da discussão ao execute)

Da raíz do **`app`** (onde vive `.planning/`):

1. **Contextualizar próximos passos**

   `/gsd-progress` — estado e phase activa  

2. **Discussão obrigatória se não há `*-CONTEXT.md` da Phase 5**

   `/gsd-discuss-phase 5`  

3. **(Opcional) Especificação escrita**

   `/gsd-spec-phase 5` — reduz ambiguidade antes do plan  

4. **Planear ondas**

   `/gsd-plan-phase 5`  

   Garante `.planning/phases/XX-refinement…/05-0{1..3}-PLAN.md`, `*-CONTEXT.md` se aplicável.

5. **Executar**

   `/gsd-execute-phase 5`  

   Ondas paralelas segundo dependências declaradas nos PLANs; flags opcionais: `--wave N`, `--gaps-only`, `--interactive`.

6. **Verificação / UAT**

   `/gsd-verify-work 5` (se aplicável)  

7. **Completar milestone / estado**

   Após verifier `passed`: GSD marca roadmap (`phase.complete`). Depois atualizar **`PROJECT.md` / REQUIREMENTS`** conforme regras de evolução do projecto.

### 4.2 Encadeamento Phase 5 com BrepGen e UI

- **Prioridade sugerida**  
  1. PLAN `05-*` já podem mencionar só **OCC** + UX; subsection “extensível BrepGen” nos SUMMARYs.  
  2. Alternativa: primeiro **épico técnico BrepGen** como fase `.2` decimal (`5.1-brepgen-worker`) usando `/gsd-insert-phase` se quiser GSD paralelo ao refinamento UX.

---

## 5. Checklist rápido “está completo quando…”

- [ ] Checkpoints BrepGen descarregados e `sample.py` validado standalone  
- [ ] Worker com flag `brepgen` + testes mocked  
- [ ] `generationConfig` (ou estrutura acordada) no payload de job até ao runner  
- [ ] PNG sob `ui_prototypes/` espelhados no shell React  
- [ ] Phase 5: `*-PLAN.md` existem, `/gsd-execute-phase 5` corrido até `*-VERIFICATION.md` **passed**

---

## Referências no repo

- Visão produto: `IDEA.md`  
- Contrato intent JSON: mesmo ficheiro, secção **IntentSchemaV1**  
- Worker stub atual: `services/worker/src/neuralcad_worker/geometry/stub_solid.py`  
- Pipeline job: `services/worker/src/neuralcad_worker/tasks/geometry.py`  
- ROADMAP: `.planning/ROADMAP.md`  
- Requirements refinamento/lint/história: `.planning/REQUIREMENTS.md` (§ Refinement…)
