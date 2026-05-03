import os

from celery import Celery

from neuralcad_worker.tasks.geometry import process_geometry_job

app = Celery(
    "neuralcad_worker",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get(
        "CELERY_RESULT_BACKEND", os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    ),
)

app.conf.update(task_track_started=True)

app.task(name="process_geometry_job")(process_geometry_job)
