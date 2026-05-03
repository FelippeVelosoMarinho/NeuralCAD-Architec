# NeuralCAD Architect — app

Co-piloto CAD (Fase 1: pipeline geométrico e plataforma).

## Local (Docker)

Copie variáveis (opcional; o `docker-compose.yml` já define valores por omissão para desenvolvimento):

```bash
cp .env.example .env
```

Subir serviços:

```bash
docker compose up --build
```

Validar configuração:

```bash
docker compose config
```

**Portas:** API **8000**, Postgres **5432** (bind em 127.0.0.1), Redis **6379** (127.0.0.1), MinIO **9000** (API S3) e **9001** (consola).

Não commite `.env` com segredos reais.

## API (rápido)

Fluxo recomendado em desenvolvimento:

1. **`POST /api/v1/intent/elicit`** — texto natural ⇒ JSON `ElicitSuccess`, ou **422** com clarificação/rejeição. Exige `ANTHROPIC_API_KEY` no ambiente (defina em `.env`; no Compose o serviço `api` propaga `ANTHROPIC_*`).

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/intent/elicit \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"caixa 100x50x25 mm","attempt":1}'
```

2. **`POST /api/v1/jobs`** — corpo `IntentJobEnvelope`: `{"intent": <IntentSchemaV1 completo>, "preflight": {"geo_risk": {...}}}` opcional. Caso o modelo devolvido no passo 1 já inclua `geo_risk`, pode reutilizar esse snapshot em `preflight`.

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/jobs \
  -H 'Content-Type: application/json' \
  -d '{"intent":{"sessionId":"demo","promptOriginal":"...","intent":{"objectType":"box","style":[],"functionalGoal":"demo"},"constraints":{"dimensionsMm":{"width":100,"height":50,"depth":25},"symmetry":"none","manufacturingHints":[],"materialHints":[]}}, "preflight":{"geo_risk":{"severity":"info","messages":["ok"]}}}'
```

- `GET /api/v1/jobs/{id}` — estado e `dimensional_audit` quando concluído.

Corpo mínimo histórico só com dimensões ao nível raíz continua a funcionar **após** uma tentativa falhada de parse e normalização legada (dims sob `intent.constraints` no bloco interno são promovidas quando necessário).

## Frontend (Vite — fase 3)

Na primeira vez:

```bash
cd services/web
npm install
# opcional: copiar exemplo de URL da API
cp .env.example .env.development.local
npm run dev
```

Abre **`http://127.0.0.1:5173`**. Por omissão, `VITE_API_BASE_URL` aponta a `http://127.0.0.1:8000`.

A API expõe **CORS** para `http://localhost:5173` e `http://127.0.0.1:5173` — necessário para chamadas desde o frontend em desenvolvimento. Para pré-visualizar STL/STEP pela API, configure no **mesmo** host que usa o Worker as variáveis `MINIO_*` (`docker-compose` já as injcta no serviço `api`).

## Licença

Ver repositório principal do projeto.
