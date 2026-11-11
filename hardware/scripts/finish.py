"""Post-routing: HV pour keepout, GND zones, stitching vias, silkscreen, DRC rules, fill. Run with kpy.sh."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from pcbnew import FromMM, VECTOR2I
from place import *

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "portail-pcb")
PCB = os.path.join(D, "portail-pcb.kicad_pcb")


def P(x, y):
    return VECTOR2I(FromMM(OX + x), FromMM(OY + y))


b = pcbnew.LoadBoard(PCB)
# --- remove previous generated items (idempotent)
for z in list(b.Zones()):
    b.RemoveNative(z)
for d in list(b.GetDrawings()):
    if d.GetClass() == "PCB_TEXT":
        b.RemoveNative(d)

gnd = b.FindNet("GND")


def poly(chain_pts):
    ch = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in chain_pts:
        ch.Append(P(x, y))
    ch.SetClosed(True)
    return ch


# HV pour keepout
z = pcbnew.ZONE(b)
z.SetIsRuleArea(True); z.SetDoNotAllowZoneFills(True)
z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
z.SetLayerSet(pcbnew.LSET.AllCuMask()); z.SetZoneName("keepout_hv_pour")
x0, y0, x1, y1 = HV_ZONE
z.Outline().AddOutline(poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))
b.Add(z)

# GND zones on both layers
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer); z.SetNet(gnd)
    z.SetMinThickness(FromMM(0.2))
    z.SetLocalClearance(FromMM(0.3))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetThermalReliefGap(FromMM(0.3)); z.SetThermalReliefSpokeWidth(FromMM(0.35))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    m = 0.4
    z.Outline().AddOutline(poly([(m, m), (W - m, m), (W - m, H - m), (m, H - m)]))
    z.SetZoneName("GND_" + ("F" if layer == pcbnew.F_Cu else "B"))
    b.Add(z)

# --- silkscreen
def text(s, x, y, size=1.0, rot=0, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s); t.SetLayer(layer)
    t.SetPosition(P(x, y))
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(0.15))
    if rot:
        t.SetTextAngleDegrees(rot)
    b.Add(t)

for (jx, labels) in ((11, ["+24V", "GND", "W.L."]), (48, ["OP-A", "OP-B", "COM"])):
    for i, l in enumerate(labels):
        text(l, jx + i * 5.08, 63.6, 0.9)
text("L", 91, 63.6, 0.9); text("N", 96.08, 63.6, 0.9)
text("230V~ DANGER", 94, 79.0, 1.0)
text("J1 ALIM / W.L.", 16, 78.9, 0.9); text("J2 COMMANDE", 53, 78.9, 0.9)
text("USB / FLASH", 9, 28, 0.9)
text("RST", 45, 36.6, 0.8); text("BOOT", 57, 36.6, 0.8)
text("ANT: U.FL", 70, 2.4, 0.8)
text("PORTAIL FAAC E045S rev A", 30, 36, 1.0)

# --- stitching vias (grid), only where clear of other copper and inside HV-free area
def clear(pt, r):
    for t in b.GetTracks():
        if t.GetNetCode() != gnd.GetNetCode() and t.HitTest(pt, r):
            return False
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() != gnd.GetNetCode() and pad.HitTest(pt, r):
                return False
        if fp.GetReference().startswith("H") and fp.GetBoundingBox(False).Inflate(FromMM(1)).Contains(pt):
            return False
        if pad_hole_near(fp, pt):
            return False
    return True

def pad_hole_near(fp, pt):
    for pad in fp.Pads():
        if pad.GetDrillSize().x > 0:
            if pad.HitTest(pt, FromMM(1.0)):
                return True
    return False

def in_zone(pt):
    return True

for t in list(b.GetTracks()):  # previous stitching vias (idempotent re-run)
    if t.GetClass() == "PCB_VIA":
        vx, vy = pcbnew.ToMM(t.GetPosition().x) - OX, pcbnew.ToMM(t.GetPosition().y) - OY
        if abs((vx - 5.0) / 8.0 - round((vx - 5.0) / 8.0)) < 1e-3 and abs((vy - 5.0) / 8.0 - round((vy - 5.0) / 8.0)) < 1e-3 \
                and t.GetNetname() == "GND":
            b.RemoveNative(t)

n = 0
x = 5.0
while x < W - 4:
    y = 5.0
    while y < H - 4:
        pt = P(x, y)
        in_hv = HV_ZONE[0] - 1 <= x and HV_ZONE[1] - 1 <= y
        sl = abs(x - SLOT[0]) < 3 and abs(y - SLOT[1]) < SLOT[3] / 2 + 3
        if not in_hv and not sl and clear(pt, FromMM(0.8)) and in_zone(pt):
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pt); v.SetNet(gnd)
            v.SetWidth(FromMM(0.6)); v.SetDrill(FromMM(0.3))
            b.Add(v); n += 1
        y += 8.0
    x += 8.0
print("stitching vias:", n)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
zs = {z.GetLayer(): z for z in b.Zones() if not z.GetIsRuleArea()}
removed = 0
for t in list(b.GetTracks()):
    if t.GetClass() == "PCB_VIA" and t.GetNetname() == "GND":
        ok = all(zs[l].HitTestFilledArea(l, t.GetPosition(), FromMM(0.3)) for l in zs)
        if not ok and not any(o is not t and o.GetNetCode() == t.GetNetCode() and o.GetClass() == "PCB_TRACK"
                              and o.HitTest(t.GetPosition(), 0) for o in b.GetTracks()):
            b.RemoveNative(t); removed += 1
print("removed dangling vias:", removed)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print("saved")
