# Worker (Celery + pythonocc-core)

Imagem base **Miniconda** com `pythonocc-core` do canal **conda-forge** (recomendado para builds reprodutíveis).

Build:

```bash
docker compose build worker
```

Se `pythonocc-core=7.7.2` falhar no resolver, trocar no Dockerfile por:

`pythonocc-core` sem pin ou `conda install -c conda-forge pythonocc-core`.
