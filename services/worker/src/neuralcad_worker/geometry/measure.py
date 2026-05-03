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


def shape_to_stl_bytes(shape) -> bytes:
    """Exporta mesh triangular em STL binário (pythonocc). Tessela antes do Write."""
    import os
    import tempfile

    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.StlAPI import StlAPI_Writer

    BRepMesh_IncrementalMesh(shape, 0.25)

    writer = StlAPI_Writer()
    fd, path = tempfile.mkstemp(suffix=".stl")
    os.close(fd)
    try:
        writer.Write(shape, path)
        with open(path, "rb") as f:
            return f.read()
    finally:
        os.unlink(path)


def topology_sketch_for_shape(shape) -> dict:
    """Contagens Face/Edge/Vertex via TopExp (MVP)."""
    from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
    from OCC.Core.TopExp import TopExp_Explorer

    def count(top_abs_enum: int) -> int:
        exp = TopExp_Explorer(shape, top_abs_enum)
        n = 0
        while exp.More():
            n += 1
            exp.Next()
        return n

    return {
        "faces": count(TopAbs_FACE),
        "edges": count(TopAbs_EDGE),
        "vertices": count(TopAbs_VERTEX),
        "confidence": "mvp",
    }
