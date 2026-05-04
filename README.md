# NeuralCAD Architect — aplicativo (`app`)

Stack local: Postgres, Redis, MinIO (S3-compatível), API FastAPI + Celery worker (`pythonocc` / OCC), SPA Vite/React.

Este documento descreve o **fluxo completo** para subir backend e frontend e validar um job até artefactos (STEP/STL).

## Pré-requisitos

- **Docker Engine** + **Compose** (plug-in).
- **Node.js 20+** (para `services/web`).
- Portas no host relativamente livres (veja secção seguinte).

## Portas no host (`docker-compose`)

| Serviço   | Binding no host por omissão | Notas |
|-----------|------------------------------|-------|
| Postgres  | `127.0.0.1:5432`             |       |
| Redis     | **`127.0.0.1:6380` → container `6379`** | Evita conflito se já tiveres Redis na 6379. Dentro da rede Docker continua-se a usar `redis:6379`. |
| MinIO     | `9000` (API), `9001` (console) |       |
| API       | **`127.0.0.1:${HOST_API_PORT:-8000}`** | Define `HOST_API_PORT` na raiz ou no `.env` se **8000** estiver ocupada. |
| Web (dev) | `5173`                        | Após `npm run dev` em `services/web`. |
| prompt-bridge | **`127.0.0.1:${HOST_PROMPT_BRIDGE_PORT:-3040}`** | Opcional (`--profile cursor`), para `PROMPT_LLM_BACKEND=cursor`. |


Passo seguinte sempre a partir da **raiz** do repositório (`.../NeuralCAD/app`).

---

## 1. Variáveis de ambiente da stack

Copia o exemplo e ajusta segredos se quiseres:

```bash
cp .env.example .env
```

- **`HOST_API_PORT`**: porta publicada no host para a API (omitir ou `8000` por omissão). Se já houver algo a ouvir em **8000**, usa por exemplo **`8010`** e alinha o frontend (passo 4).
- **Prompt Architect (LLM)**:
  - **Anthropic (omissão):** **`ANTHROPIC_API_KEY`** no `.env` e **`PROMPT_LLM_BACKEND=anthropic`** (ou omitido).
  - **Cursor SDK:** **`PROMPT_LLM_BACKEND=cursor`**, **`CURSOR_PROMPT_BRIDGE_URL`** (depende do sítio onde corre a API — vê **[Prompt-bridge Cursor (elicitation)](#prompt-bridge-cursor-elicitation)** abaixo), **`CURSOR_API_KEY`**, e levantar a stack com **`docker compose --profile cursor up --build`** (o serviço `prompt-bridge` só existe com o **profile `cursor`**; corre `Agent.prompt` via `@cursor/sdk` sobre o repo em `/workspace`).

Validar o compose:

```bash
docker compose config
```

---

## 2. Subir backend (API + worker + dados)

Build e arranque em primeiro plano (logs visíveis):

```bash
docker compose up --build
```

Ou em segundo plano:

```bash
docker compose up -d --build
```

Aguarda até os healthchecks do Postgres e do Redis ficarem **`healthy`** e a API responder.

### Conflitos de porta

| Problema | Resolução |
|----------|-----------|
| **Redis 6379** já em uso no host | O projeto já expõe Redis em **`127.0.0.1:6380`**. Dentro dos containers **`REDIS_URL` continua `redis://redis:6379/0`**. |
| **API 8000** ocupada | `export HOST_API_PORT=8010` (ou coloca no `.env`) e `docker compose up --build` de novo. Health: `http://127.0.0.1:8010/health`. |

---

## Prompt-bridge Cursor (elicitation)

O endpoint de **elicitation** pode usar o backend **`PROMPT_LLM_BACKEND=cursor`**, que fala HTTP com o **`prompt-bridge`** (serviço Node em `services/prompt-bridge/`).

### Quando aparece `503` / `cursor prompt-bridge unreachable: ... Temporary failure in name resolution` (`[Errno -3]`)?

Isso é **erro de DNS**: o cliente HTTP (FastAPI/`httpx`) tentou resolver o hostname **`prompt-bridge`** **fora** da rede Docker. Esse nome **só existe entre containers Compose** — na tua máquina nem sempre resolve.

Normalmente é **mal configurado**, não um “bridge corrompido”. Não precisas de reinstalar o SDK; corrige URL e serviços.

### Passo a passo (rápido)

1. **Garantir que o bridge está mesmo a arrancar**
   ```bash
   docker compose --profile cursor up -d --build prompt-bridge
   ```
   Ou stack completa: `docker compose --profile cursor up -d --build`

2. **Provar que o bridge responde no host** (usa a porta [`HOST_PROMPT_BRIDGE_PORT`](#portas-no-host-docker-compose), por omissão **3040**):
   ```bash
   PB="${HOST_PROMPT_BRIDGE_PORT:-3040}"
   curl -sS "http://127.0.0.1:${PB}/health"
   ```
   Esperado: JSON com `"service":"neuralcad-prompt-bridge"` (e `CURSOR_API_KEY` definido no Compose para uso real do `/v1/complete`, senão verás erro noutro formato).

3. **Definir `CURSOR_PROMPT_BRIDGE_URL` conforme onde corre a FastAPI:**
   | Onde está a API | Valor típico de `CURSOR_PROMPT_BRIDGE_URL` |
   |---|---|
   | **Container `api`** (Compose, como no `docker-compose.yml`) | `http://prompt-bridge:3040` (valor por omissão no compose — resolve na rede Docker) |
   | **Host** (`uvicorn` / IDE a correr código em `services/api` à mão) | `http://127.0.0.1:${HOST_PROMPT_BRIDGE_PORT:-3040}` — **obrigatório** usar `127.0.0.1` ou `localhost`, **nunca** `prompt-bridge` |

4. Reiniciar só o necessário (`api` ou o processo uvicorn local) para carregar o `.env`.

5. Se **não** quiseres o Cursor neste momento, usa apenas Anthropic: no `.env` **`PROMPT_LLM_BACKEND=anthropic`** e **`ANTHROPIC_API_KEY`** — o bridge deixa de ser necessário para elicitation.

### Notas

- **`--profile cursor`**: sem este perfil, o serviço `prompt-bridge` **nem sequer existe** na stack (`docker compose`). Nesse caso até `127.0.0.1:3040` pode falhar (connection refused).
- **`CURSOR_API_KEY`**: chave válida Cursor no `.env` passada ao compose; caso contrário o bridge pode devolver erro ao chamar `/v1/complete` com problemas diferentes de rede.

---

## 3. Verificação rápida da API

```bash
API_PORT="${HOST_API_PORT:-8000}"
curl -sS "http://127.0.0.1:${API_PORT}/health"
```

Resposta esperada: JSON com `"status":"ok"` (ou equivalente definido pela app).

---

## 4. Frontend (SPA)

Noutro terminal:

```bash
cd services/web
npm install
```

Cria `.env.development.local` se ainda não existir — a **URL da API** tem de bater certo com a porta do passo 2:

```bash
# Exemplo se a API estiver em 8000 (omissão)
echo 'VITE_API_BASE_URL=http://127.0.0.1:8000' > .env.development.local

# Se usaste HOST_API_PORT=8010:
# echo 'VITE_API_BASE_URL=http://127.0.0.1:8010' > .env.development.local
```

Arranque em desenvolvimento:

```bash
npm run dev
```

Abre o URL que o Vite indicar (normalmente `http://127.0.0.1:5173`).

---

## 5. Verificação ponta-a-ponta (job + artefactos)

Com a stack de pé, podes criar um job e ir às rotas de artefactos. Exemplo mínimo (substitui `API_PORT` se necessário):

```bash
API_PORT="${HOST_API_PORT:-8000}"
BASE="http://127.0.0.1:${API_PORT}"

JOB_ID=$(curl -sS -X POST "$BASE/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{"spec":"caixa 10x20x30 mm","language":"pt"}' | jq -r '.id')

# Poll até status success (ajusta o sleep/repetições conforme a carga)
for i in $(seq 1 60); do
  S=$(curl -sS "$BASE/api/v1/jobs/$JOB_ID" | jq -r '.status')
  echo "status=$S"
  [ "$S" = "success" ] && break
  sleep 2
done

curl -sS -o /tmp/out.step "$BASE/api/v1/jobs/$JOB_ID/artifacts/step"
curl -sS -o /tmp/out.stl  "$BASE/api/v1/jobs/$JOB_ID/artifacts/stl"

wc -c /tmp/out.step /tmp/out.stl
```

Esperado: **`success`**, STEP e STL com **tamanho em bytes maior que zero** (o STL depende da malha tessellada antes da exportação no worker OCC).

---

## 6. Parar a stack

```bash
docker compose down
```

Volumes nomeados mantêm dados de Postgres/MinIO até os apagares explicitamente.

---

## Estrutura útil

- `services/api` — FastAPI, filas Celery, MinIO.
- `services/worker` — worker Celery, geometria OCC, export STEP/STL.
- `services/web` — UI Vite/React (Monaco, R3F).

Para detalhes de API e variáveis, vê também `services/api/README.md` e `services/worker/README.md`.
