"""Task Celery `process_geometry_job` — geometria stub, STEP, MinIO, audit dimensional."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from neuralcad_worker.db.sync_session import Job, sync_session
from neuralcad_worker.geometry.measure import (
    measure_bbox_mm,
    shape_to_step_bytes,
    shape_to_stl_bytes,
    topology_sketch_for_shape,
)
from neuralcad_worker.geometry.stub_solid import build_box_shape
from neuralcad_worker.realtime import build_envelope, publish
from neuralcad_worker.storage.minio_client import ensure_bucket, get_s3_client, put_object_bytes

DEFAULT_WHD = (10.0, 20.0, 30.0)


def _lifecycle(job_id: str, phase: str) -> None:
    publish(job_id, build_envelope(job_id, "job.lifecycle", {"lifecycle": phase}))


def _progress(job_id: str, pipeline_stage: str) -> None:
    publish(job_id, build_envelope(job_id, "job.progress", {"pipelineStage": pipeline_stage}))


def _reload_job_status(SessionFactory: type, uid: uuid.UUID) -> str | None:
    with SessionFactory() as session:
        job = session.get(Job, uid)
        return job.status if job is not None else None


def _parse_target_dims(payload: dict | None) -> tuple[float, float, float, dict | None]:
    """
    Extrai dims alvo desde ``payload_json``.

    Preferência (**Fase 2 / IDEA**): ``constraints.dimensionsMm`` ao nível raiz.
    **Legado:** ``intent.constraints.dimensionsMm`` quando o primeiro não está completo (Fase 1).
    """
    if not payload:
        return (*DEFAULT_WHD, None)

    dims: dict = {}
    rc = payload.get("constraints") if isinstance(payload.get("constraints"), dict) else None
    if rc and isinstance(rc.get("dimensionsMm"), dict):
        dims = rc["dimensionsMm"]

    intent_block = payload.get("intent") if isinstance(payload.get("intent"), dict) else None
    if intent_block:
        nc = intent_block.get("constraints")
        if isinstance(nc, dict) and isinstance(nc.get("dimensionsMm"), dict):
            merged = nc["dimensionsMm"]
            need = ("width", "height", "depth")
            if not all(isinstance(dims.get(k), (int, float)) for k in need):
                dims = merged

    w, h, depth = dims.get("width"), dims.get("height"), dims.get("depth")
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

    _lifecycle(job_id, "running")
    _progress(job_id, "PROMPTING")

    def _blocked_by_cancel(stage_after: str) -> bool:
        st = _reload_job_status(SessionFactory, uid)
        if st != "cancelled":
            return False
        _lifecycle(job_id, "cancelled")
        _ = stage_after
        return True

    if _blocked_by_cancel("running"):
        return

    _progress(job_id, "DENOISING_FACES")
    if _blocked_by_cancel("DENOISING_FACES"):
        return

    w_mm, h_mm, d_mm, target_obj = _parse_target_dims(payload)

    try:
        shape = build_box_shape(w_mm, h_mm, d_mm)
    except Exception as e:  # noqa: BLE001
        err = str(e)[:2000]
        _lifecycle(job_id, "failed")
        with SessionFactory() as session:
            job = session.get(Job, uid)
            if job is not None:
                job.status = "failed"
                job.error_message = err
                job.updated_at = datetime.now(timezone.utc)
                session.commit()
        return

    _progress(job_id, "DENOISING_EDGES")
    if _blocked_by_cancel("DENOISING_EDGES"):
        return

    try:
        step_bytes = shape_to_step_bytes(shape)
        measured = measure_bbox_mm(shape)
    except Exception as e:  # noqa: BLE001
        err = str(e)[:2000]
        _lifecycle(job_id, "failed")
        with SessionFactory() as session:
            job = session.get(Job, uid)
            if job is not None:
                job.status = "failed"
                job.error_message = err
                job.updated_at = datetime.now(timezone.utc)
                session.commit()
        return

    _progress(job_id, "SEWING")
    if _blocked_by_cancel("SEWING"):
        return

    bucket = os.environ.get("MINIO_BUCKET", "neuralcad-artifacts")
    artifact_key = f"jobs/{job_id}/model.step"
    client = get_s3_client()
    ensure_bucket(client, bucket)
    put_object_bytes(client, bucket, artifact_key, step_bytes, "application/step")

    topology_sketch = topology_sketch_for_shape(shape)
    mesh_error: str | None = None
    try:
        stl_bytes = shape_to_stl_bytes(shape)
        stl_key = f"jobs/{job_id}/model.stl"
        put_object_bytes(client, bucket, stl_key, stl_bytes, "model/stl")
    except Exception as e:  # noqa: BLE001
        mesh_error = str(e)[:500]

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
        "topologySketch": topology_sketch,
    }
    if mesh_error:
        audit["mesh_error"] = mesh_error

    _progress(job_id, "MEASURING_ABNT")
    if _blocked_by_cancel("MEASURING_ABNT"):
        return

    _lifecycle(job_id, "success")

    with SessionFactory() as session:
        job = session.get(Job, uid)
        if job is None:
            return
        job.status = "success"
        job.artifact_key = artifact_key
        job.dimensional_audit = audit
        job.updated_at = datetime.now(timezone.utc)
        session.commit()
