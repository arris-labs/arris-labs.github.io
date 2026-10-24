# A motor-mount bracket in arris.build: an L plate, a boss, a bore and a
# bolt pattern cut in one call, fillets on the bend and the counterbore rims,
# and a chamfer on the boss. Every face is tagged by the operation that made
# it; a tag follows its faces through every later operation.

import arris
from arris.build import Solid, Workplane

LABELS = ["plate", "boss", "bore", "bolt holes", "counterbores", "bend fillet", "rim fillets", "chamfer"]


def labelled(solid, name):
    # Tag every face no tag names yet: the faces the last operation made.
    seen = set().union(*solid.tags.values()) if solid.tags else set()
    return solid.tag(name, [face for face in solid.faces() if face not in seen])


def build():
    # The plate: an L profile in the xz plane, extruded along y.
    plate = Workplane.XZ().polygon([(0, 0), (60, 0), (60, 8), (8, 8), (8, 50), (0, 50)]).extrude(-40)
    part = labelled(plate, "plate")

    # A boss on the upright leg, then the bore and bolt pattern in one cut.
    boss = labelled(Solid.cylinder((8, 20, 32), (1, 0, 0), 14, 12), "boss")
    part = labelled(part.fuse(boss), "boss")
    bore = labelled(Solid.cylinder((-1, 20, 32), (1, 0, 0), 8, 23), "bore")
    holes = [labelled(Solid.cylinder((40, y, -1), (0, 0, 1), 3.5, 10), "bolt holes") for y in (8, 32)]
    wells = [labelled(Solid.cylinder((40, y, 5), (0, 0, 1), 6, 4), "counterbores") for y in (8, 32)]
    part = labelled(part.cut(bore, holes[0], wells[0], holes[1], wells[1]), "bolt holes")

    # Fillets and the chamfer: each edge picked by what made it, never by index.
    bend = part.edges().from_role(arris.Role("extrude", "Rise", 0, 3)).one()
    part = labelled(part.fillet([bend], 4), "bend fillet")
    faces = part.faces()
    rims = faces.tagged("plate").edges() & faces.tagged("counterbores").edges()
    part = labelled(part.fillet(rims, 0.8), "rim fillets")
    faces = part.faces().tagged("boss")
    lip = faces.kind("plane").edges() & faces.kind("cylinder").edges()
    return labelled(part.chamfer([lip.one()], 1.5), "chamfer")


if __name__ == "__main__":
    part = build()
    print(part.measure())
    part.export_step("bracket.step")
