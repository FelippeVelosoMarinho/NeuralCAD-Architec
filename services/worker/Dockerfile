FROM continuumio/miniconda3:24.1.2-0

WORKDIR /app

RUN conda install -y -c conda-forge \
    python=3.10 \
    pythonocc-core=7.7.2 \
    pip \
    && conda clean -afy

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app/src

CMD ["celery", "-A", "neuralcad_worker.celery_app", "worker", "--loglevel=info"]
