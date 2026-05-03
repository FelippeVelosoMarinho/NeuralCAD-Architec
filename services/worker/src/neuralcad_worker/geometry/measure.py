"""Medição de bounding box em mm (convenção fixa do protótipo)."""

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add


def measure_bbox_mm(shape) -> dict[str, float]:
    """
    Devolve extents alinhados aos eixos mundiais:
    width = xmax - xmin, height = ymax - ymin, depth = zmax - zmin.
    """
    box = Bnd_Box()
    brepbndlib_Add(shape, box)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return {
        "width": float(xmax - xmin),
        "height": float(ymax - ymin),
        "depth": float(zmax - zmin),
    }


def shape_to_step_bytes(shape) -> bytes:
    import os
    import tempfile

    from OCC.Core.IFSelect import IFSelect_RetDone
    from OCC.Core.STEPControl import STEPControl_AsIs, STEPControl_Writer

    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    fd, path = tempfile.mkstemp(suffix=".step")
    os.close(fd)
    try:
        st = writer.Write(path)
        if st != IFSelect_RetDone:
            raise RuntimeError(f"STEP export failed with status {st}")
        with open(path, "rb") as f:
            return f.read()
    finally:
        os.unlink(path)
