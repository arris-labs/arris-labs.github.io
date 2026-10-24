"""Exports the showcase bracket for the viewer.

    pip install arris==0.9.1
    python tools/export.py

writes into `assets/`:

- `bracket.py`, the script that builds the part (shown on the page);
- `bracket.bin`, the mesh: a header of four little-endian u32 (vertex,
  triangle and edge-segment counts, then 0), the f32 vertex positions, the
  u32 triangle indices, the f32 edge segments (two points each) and one u8
  label per vertex. Vertices are split per face, so normals stay smooth
  within a face and crisp across an edge;
- `bracket.json`, the label names, colours, mass properties and counts;
- `bracket.step`, the part as AP214.

Deterministic: rerunning with the same arris version leaves every file
unchanged.
"""

import importlib.metadata
import json
import runpy
import struct
from pathlib import Path

import arris

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SCRIPT = ASSETS / "bracket.py"
CHORD = 0.005

# One colour per label, the palette of the README's showcase render.
PALETTE = ["#96a0af", "#3c82c8", "#e18228", "#50af6e", "#be50a0", "#e1be32", "#3cafb9", "#d25046"]


def u32s(data):
    return struct.unpack(f"<{len(data) // 4}I", data)


def f64s(data):
    return struct.unpack(f"<{len(data) // 8}d", data)


def main():
    namespace = runpy.run_path(str(SCRIPT))
    labels, part = namespace["LABELS"], namespace["build"]()
    part.check("full")

    mesh = part.mesh(CHORD)
    points = f64s(mesh.positions)
    triangles = u32s(mesh.triangles)
    label_of = {face: labels.index(name) for name, faces in part.tags.items() for face in faces}

    # Split the vertices per face: a vertex on an edge gets one copy per face.
    positions, indices, vertex_labels = [], [], []
    for face, start, stop in mesh.faces:
        local = {}
        for corner in triangles[3 * start : 3 * stop]:
            if corner not in local:
                local[corner] = len(vertex_labels)
                positions.extend(points[3 * corner : 3 * corner + 3])
                vertex_labels.append(label_of[face])
            indices.append(local[corner])

    edge_indices = u32s(mesh.edge_indices)
    segments = []
    for _edge, start, stop in mesh.edges:
        run = edge_indices[start:stop]
        for a, b in zip(run, run[1:]):
            segments.extend(points[3 * a : 3 * a + 3])
            segments.extend(points[3 * b : 3 * b + 3])

    n_vertices, n_triangles, n_segments = len(vertex_labels), len(indices) // 3, len(segments) // 6
    blob = struct.pack("<4I", n_vertices, n_triangles, n_segments, 0)
    blob += struct.pack(f"<{len(positions)}f", *positions)
    blob += struct.pack(f"<{len(indices)}I", *indices)
    blob += struct.pack(f"<{len(segments)}f", *segments)
    blob += bytes(vertex_labels)
    (ASSETS / "bracket.bin").write_bytes(blob)

    mass = part.measure()
    meta = {
        "arris": importlib.metadata.version("arris"),
        "labels": [{"name": n, "colour": c} for n, c in zip(labels, PALETTE)],
        "faces": len(mesh.faces),
        "edges": len(mesh.edges),
        "triangles": n_triangles,
        "chord": CHORD,
        "volume": round(mass.volume, 3),
        "area": round(mass.area, 3),
        "centroid": [round(c, 3) for c in mass.centroid],
    }
    (ASSETS / "bracket.json").write_text(json.dumps(meta, indent=1) + "\n")
    part.export_step(ASSETS / "bracket.step")
    print(f"{n_vertices} vertices, {n_triangles} triangles, {n_segments} edge segments, {len(blob)} bytes")


if __name__ == "__main__":
    assert arris is not None
    main()
