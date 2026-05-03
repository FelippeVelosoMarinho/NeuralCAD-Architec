"""Task Celery `process_geometry_job` — geometria stub, STEP, MinIO, audit dimensional."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from neuralcad_worker.db.sync_session import Job, sync_session
from neuralcad_worker.geometry.measure import measure_bbox_mm, shape_to_step_bytes
from neuralcad_worker.geometry.stub_solid import build_box_shape
from neuralcad_worker.storage.minio_client import ensure_bucket, get_s3_client, put_object_bytes

DEFAULT_WHD = (10.0, 20.0, 30.0)


def _parse_target_dims(payload: dict | None) -> tuple[float, float, float, dict | None]:
    if not payload:
        return (*DEFAULT_WHD, None)
    intent = payload.get("intent") or {}
    constraints = intent.get("constraints") or {}
    d = constraints.get("dimensionsMm") or {}
    w, h, depth = d.get("width"), d.get("height"), d.get("depth")
    if w is not None and h is not None and depth is not None:
        target = {"dimensionsMm": {"width": float(w), "height": float(h), "depth": float(depth)}}
        return float(w), float(h), float(depth), target
    return (*DEFAULT_WHD, None)


def _tolerance_ok(measured: float, target: float) -> bool:
    if target <= 0:
        return True
    return abs(measured - target) <= max(0.5, 0.01 * target)


def process_geometry_job(job_id: str) -> None:
    SessionFactory = sync_session()
    uid = uuid.UUID(job_id)
    payload: dict | None
    with SessionFactory() as session:
        job = session.get(Job, uid)
        if job is None:
            return
        job.status = "running"
        job.updated_at = datetime.now(timezone.utc)
        payload = job.payload_json
        session.commit()

    w_mm, h_mm, d_mm, target_obj = _parse_target_dims(payload)

    try:
        shape = build_box_shape(w_mm, h_mm, d_mm)
        step_bytes = shape_to_step_bytes(shape)
        measured = measure_bbox_mm(shape)
    except Exception as e:  # noqa: BLE001
        err = str(e)[:2000]
        with SessionFactory() as session:
            job = session.get(Job, uid)
            if job is not None:
                job.status = "failed"
                job.error_message = err
                job.updated_at = datetime.now(timezone.utc)
                session.commit()
        return

    bucket = os.environ.get("MINIO_BUCKET", "neuralcad-artifacts")
    artifact_key = f"jobs/{job_id}/model.step"
    client = get_s3_client()
    ensure_bucket(client, bucket)
    put_object_bytes(client, bucket, artifact_key, step_bytes, "application/step")

    measured_block: dict = {
        "bbox_mm": measured,
        "source": "pythonocc",
        "measured_at": datetime.now(timezone.utc).isoformat(),
    }

    delta = None
    overall_within_tolerance = None
    if target_obj:
        td = target_obj["dimensionsMm"]
        delta = {
            "width_mm": measured["width"] - td["width"],
            "height_mm": measured["height"] - td["height"],
            "depth_mm": measured["depth"] - td["depth"],
        }
        overall_within_tolerance = all(
            _tolerance_ok(measured[k], td[k]) for k in ("width", "height", "depth")
        )

    audit: dict = {
        "target": target_obj,
        "measured": measured_block,
        "delta": delta,
        "withinTolerance": overall_within_tolerance,
        "thickness_mm": None,
        "thickness_reason": "not_implemented",
    }

    with SessionFactory() as session:
        job = session.get(Job, uid)
        if job is None:
            return
        job.status = "success"
        job.artifact_key = artifact_key
        job.dimensional_audit = audit
        job.updated_at = datetime.now(timezone.utc)
        session.commit()
