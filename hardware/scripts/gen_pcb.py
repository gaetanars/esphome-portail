"""Generate portail-pcb.kicad_pcb (placement + outline + slot). Run with kpy.sh."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from pcbnew import FromMM, VECTOR2I
import design
from place import *
from sexpr import FPDIR

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "portail-pcb", "portail-pcb.kicad_pcb")


def P(x, y):
    return VECTOR2I(FromMM(OX + x), FromMM(OY + y))


def line(b, x1, y1, x2, y2, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2))
    s.SetLayer(layer); s.SetWidth(FromMM(w))
    b.Add(s)


def arc(b, cx, cy, sx, sy, ex, ey):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    # centre/start/end constructor semantic: use three-point
    import math
    r = math.hypot(sx - cx, sy - cy)
    a1 = math.atan2(sy - cy, sx - cx); a2 = math.atan2(ey - cy, ex - cx)
    am = (a1 + a2) / 2
    if abs(a1 - a2) > math.pi:
        am += math.pi
    mx, my = cx + r * math.cos(am), cy + r * math.sin(am)
    s.SetArcGeometry(P(sx, sy), P(mx, my), P(ex, ey))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1))
    b.Add(s)


def outline(b, w, h, r=2.0):
    line(b, r, 0, w - r, 0); line(b, w, r, w, h - r)
    line(b, w - r, h, r, h); line(b, 0, h - r, 0, r)
    arc(b, r, r, r, 0, 0, r); arc(b, w - r, r, w, r, w - r, 0)
    arc(b, w - r, h - r, w - r, h, w, h - r); arc(b, r, h - r, 0, h - r, r, h)


def slot(b, cx, cy, sw, sl):
    r = sw / 2
    x1, x2, y1, y2 = cx - r, cx + r, cy - sl / 2 + r, cy + sl / 2 - r
    line(b, x1, y1, x1, y2); line(b, x2, y1, x2, y2)
    arc(b, cx, y1, x1, y1, x2, y1); arc(b, cx, y2, x2, y2, x1, y2)


def keepout(b, x0, y0, x1, y1, name, tracks):
    z = pcbnew.ZONE(b)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(tracks); z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask())
    z.SetZoneName(name)
    ch = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        ch.Append(P(x, y))
    ch.SetClosed(True)
    z.Outline().AddOutline(ch)
    b.Add(z)


def build():
    b = pcbnew.CreateEmptyBoard()
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(2) if hasattr(ds, "SetCopperLayerCount") else b.SetCopperLayerCount(2)
    nets = {}
    for p in design.PARTS:
        for n in p["pins"].values():
            if n not in nets:
                ni = pcbnew.NETINFO_ITEM(b, n)
                b.Add(ni)
                nets[n] = ni
    from sexpr import get_symbol, pins as sympins
    for p in design.PARTS:
        if p.get("mech"):
            continue
        l, s = p["sym"].split(":")
        for num, (pname, *_r) in sympins(get_symbol(l, s)).items():
            if num not in p["pins"]:
                nn = f"unconnected-({p['ref']}-{pname}-Pad{num})" if pname else f"unconnected-({p['ref']}-Pad{num})"
                p["pins"][num] = nn
                ni = pcbnew.NETINFO_ITEM(b, nn)
                b.Add(ni)
                nets[nn] = ni
    for p in design.PARTS:
        lib, name = p["fp"].split(":")
        fp = pcbnew.FootprintLoad(f"{FPDIR}/{lib}.pretty", name)
        fp.SetReference(p["ref"]); fp.SetValue(p["value"])
        x, y, rot = PLACE[p["ref"]]
        fp.SetPosition(P(x, y))
        if rot:
            fp.SetOrientationDegrees(rot)
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        for pad in list(fp.Pads()):
            if pad.GetDrillSize().x and pad.GetDrillSize().x < FromMM(0.3) and pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                fp.Remove(pad)  # 0.2 mm thermal vias of the ESP32 EPAD: below PCBWay standard drill
                continue
            n = p["pins"].get(pad.GetNumber())
            if n:
                pad.SetNet(nets[n])
        for fname, fval in (("Manufacturer", p["mfr"]), ("MPN", p["mpn"])):
            fp.SetField(fname, fval)
            fp.GetField(fname).SetVisible(False)
        if p.get("mech"):
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM)
        fp.Value().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(FromMM(0.8), FromMM(0.8)))
        fp.Reference().SetTextThickness(FromMM(0.12))
        b.Add(fp)
    outline(b, W, H)
    slot(b, SLOT[0], SLOT[1], SLOT[2], SLOT[3])
    sx, sy, sw, sl = SLOT
    # no LV copper over the slot ends (would shorten the creepage path around the slot)
    keepout(b, sx - 2.4, HV_ZONE[1], sx + 3.0, sy - sl / 2 + 0.5, "keepout_slot_top", tracks=True)
    keepout(b, sx - 2.4, sy + sl / 2 - 0.5, sx + 3.0, H, "keepout_slot_bottom", tracks=True)
    keepout(b, SLOT[0] - SLOT[2] / 2 - 0.3, SLOT[1] - SLOT[3] / 2 - 0.3, SLOT[0] + SLOT[2] / 2 + 0.3,
            SLOT[1] + SLOT[3] / 2 + 0.3, "keepout_slot", tracks=True)
    b.Save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    build()
