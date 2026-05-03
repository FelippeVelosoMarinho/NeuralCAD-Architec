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

- `POST /api/v1/jobs` — corpo JSON opcional (ex.: `{"intent":{"constraints":{"dimensionsMm":{"width":10,"height":20,"depth":30}}}}`)
- `GET /api/v1/jobs/{id}` — estado e `dimensional_audit` quando concluído

## Licença

Ver repositório principal do projeto.
