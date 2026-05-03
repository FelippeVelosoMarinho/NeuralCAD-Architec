"""Caixa trivial em OCC (protótipo — substituir por BrepGen na fase seguinte)."""

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.TopoDS import TopoDS_Shape


def build_box_shape(dx_mm: float, dy_mm: float, dz_mm: float) -> TopoDS_Shape:
    """Constrói um sólido caixa com arestas alinhadas aos eixos XYZ (mm)."""
    return BRepPrimAPI_MakeBox(float(dx_mm), float(dy_mm), float(dz_mm)).Shape()
