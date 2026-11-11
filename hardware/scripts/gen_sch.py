"""Generate portail-pcb.kicad_sch from design.py (labels-based schematic)."""
import math, sys, uuid, os
sys.path.insert(0, os.path.dirname(__file__))
from sexpr import *
import design

OUT = os.path.join(os.path.dirname(__file__), "..", "portail-pcb", "portail-pcb.kicad_sch")
ROOT = "7f0c2a4e-5b1d-4c3a-9e77-0a1b2c3d4e5f"
NS = uuid.UUID(ROOT)


def uid(*a):
    return str(uuid.uuid5(NS, "/".join(map(str, a))))


# Block origins (mm) and local layout
BLOCKS = {
    "power": (15.24, 25.4),
    "usb": (15.24, 215.9),
    "esp": (200.66, 25.4),
    "relay": (200.66, 190.5),
    "wl": (385.06, 25.4),
    "lamp": (385.06, 110.0),
}
TITLES = {"power": "ALIMENTATION 24 V -> 5 V -> 3,3 V", "usb": "USB-C / CH340C / AUTO-RESET",
          "esp": "ESP32-WROOM-32UE (antenne U.FL)", "relay": "SORTIES RELAIS OP-A / OP-B (contacts secs)",
          "wl": "RETOUR W.L. (24 V, opto)", "lamp": "RETOUR LAMP (230 V~, opto AC) - ZONE DANGEREUSE"}


def snap(v):
    return round(v / 1.27) * 1.27


def xform(px, py, rot):
    t = math.radians(rot)
    return (px * math.cos(t) - py * math.sin(t), px * math.sin(t) + py * math.cos(t))


def build():
    libsyms = {}
    out = [Sym("kicad_sch"), [Sym("version"), 20260101], [Sym("generator"), "gen_sch"],
           [Sym("generator_version"), "10.0"], [Sym("uuid"), ROOT], [Sym("paper"), "A2"]]
    out.append([Sym("title_block"), [Sym("title"), "Portail FAAC E045S - carte ESP32"],
                [Sym("rev"), "A"], [Sym("comment"), 1, "Pilotage 2 relais + retour W.L./LAMP"]])
    body = []
    # layout cursors per block
    cur = {b: [0, 0] for b in BLOCKS}
    big = {"U1", "U2", "U3", "U4", "U5", "J4", "K1", "K2", "U6", "U7", "Q1", "Q2", "Q3", "Q4", "J1", "J2", "J3"}
    placed = {}
    # IC column positions
    ic_pos = {"J1": (30, 15), "U1": (60, 45), "U2": (60, 85), "J4": (30, 40), "U3": (40, 80), "U4": (100, 60),
              "Q1": (30, 125), "Q2": (100, 125), "U5": (60, 60), "K1": (40, 20), "K2": (40, 70), "J2": (40, 120),
              "Q3": (110, 30), "Q4": (110, 80), "U6": (30, 25), "J3": (30, 20), "U7": (60, 45)}
    pas_origin = {"power": (130, 0), "usb": (180, 0), "esp": (130, 0), "relay": (150, 0), "wl": (110, 0), "lamp": (120, 0)}
    ncount = {}
    for part in design.PARTS:
        ref, lib = part["ref"], part["sym"]
        if lib not in libsyms:
            l, s = lib.split(":")
            sy = get_symbol(l, s)
            sy = [Sym("symbol"), lib] + sy[2:]
            libsyms[lib] = sy
        sy = libsyms[lib]
        pn = pins(sy)
        bx, by = BLOCKS[part["block"]]
        if part.get("mech"):
            i = int(ref[1:])
            x, y, rot = 560 + 0, 20 + 15 * i, 0
        elif ref in ic_pos:
            ox, oy = ic_pos[ref]
            x, y, rot = bx + ox, by + oy, 0
        else:
            n = ncount.get(part["block"], 0)
            ncount[part["block"]] = n + 1
            col, row = divmod(n, 12 if part["block"] in ("power", "usb") else 10)
            x = bx + pas_origin[part["block"]][0] + col * 55
            y = by + row * 14
            rot = 90 if lib in ("Device:R", "Device:C", "Device:L", "Device:Polyfuse", "Device:Varistor") else 0
        x, y = snap(x), snap(y)
        placed[ref] = (x, y, rot)
        isp = rot == 90
        props = []
        def prop(name, val, dx, dy, hide=False):
            eff = [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]]]
            if hide:
                eff.append([Sym("hide"), Sym("yes")])
            props.append([Sym("property"), name, val, [Sym("at"), x + dx, y + dy, 0], eff])
        prop("Reference", ref, 0, -5.08 if isp else -12.7)
        prop("Value", part["value"], 0, 5.08 if isp else 12.7)
        prop("Footprint", part["fp"], 0, 0, True)
        prop("Datasheet", "", 0, 0, True)
        prop("Manufacturer", part["mfr"], 0, 0, True)
        prop("MPN", part["mpn"], 0, 0, True)
        inst = [Sym("symbol"), [Sym("lib_id"), lib], [Sym("at"), x, y, rot], [Sym("unit"), 1],
                [Sym("exclude_from_sim"), Sym("no")], [Sym("in_bom"), Sym("no" if part.get("mech") else "yes")],
                [Sym("on_board"), Sym("yes")], [Sym("dnp"), Sym("no")], [Sym("uuid"), uid("sym", ref)]] + props
        for num in pn:
            inst.append([Sym("pin"), num, [Sym("uuid"), uid("pin", ref, num)]])
        inst.append([Sym("instances"), [Sym("project"), "portail-pcb",
                    [Sym("path"), "/" + ROOT, [Sym("reference"), ref], [Sym("unit"), 1]]]])
        body.append(inst)
        # labels / no-connects
        nets = part["pins"]
        for num, (name, px, py, ang, ptype, ln) in pn.items():
            X, Y = xform(px, py, rot)
            ex, ey = round(x + X, 4), round(y - Y, 4)
            if num in nets:
                lrot = int((ang + rot + 180) % 360)
                just = [Sym("justify"), Sym("left"), Sym("bottom")] if lrot in (0, 90) else [Sym("justify"), Sym("right"), Sym("bottom")]
                if lrot in (90, 270):
                    just = [Sym("justify"), Sym("left"), Sym("bottom")]
                body.append([Sym("global_label"), nets[num], [Sym("shape"), Sym("passive")],
                             [Sym("at"), ex, ey, lrot],
                             [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]], just],
                             [Sym("uuid"), uid("lbl", ref, num)],
                             [Sym("property"), "Intersheetrefs", "${INTERSHEET_REFS}", [Sym("at"), ex, ey, 0],
                              [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]], [Sym("hide"), Sym("yes")]]]])
            elif not part.get("mech") and ptype != "no_connect":
                body.append([Sym("no_connect"), [Sym("at"), ex, ey], [Sym("uuid"), uid("nc", ref, num)]])
            elif ptype == "no_connect":
                pass
    # PWR_FLAGs
    if "power:PWR_FLAG" not in libsyms:
        sy = get_symbol("power", "PWR_FLAG")
        libsyms["power:PWR_FLAG"] = [Sym("symbol"), "power:PWR_FLAG"] + sy[2:]
    for i, (net, ref) in enumerate(design.PWR_FLAGS.items(), 1):
        part = next(p for p in design.PARTS if p["ref"] == ref)
        num = next(n for n, nn in part["pins"].items() if nn == net)
        sy = libsyms[part["sym"]]
        name, px, py, ang, *_ = pins(sy)[num]
        x, y, rot = placed[ref]
        X, Y = xform(px, py, rot)
        ex, ey = round(x + X, 4), round(y - Y, 4)
        fref = f"#FLG{i:02d}"
        eff = [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]], [Sym("hide"), Sym("yes")]]
        body.append([Sym("symbol"), [Sym("lib_id"), "power:PWR_FLAG"], [Sym("at"), ex, ey, 0], [Sym("unit"), 1],
                     [Sym("exclude_from_sim"), Sym("no")], [Sym("in_bom"), Sym("no")], [Sym("on_board"), Sym("no")],
                     [Sym("dnp"), Sym("no")], [Sym("uuid"), uid("flg", i)],
                     [Sym("property"), "Reference", fref, [Sym("at"), ex, ey, 0], eff],
                     [Sym("property"), "Value", "PWR_FLAG", [Sym("at"), ex, ey, 0], eff],
                     [Sym("pin"), "1", [Sym("uuid"), uid("flgpin", i)]],
                     [Sym("instances"), [Sym("project"), "portail-pcb",
                      [Sym("path"), "/" + ROOT, [Sym("reference"), fref], [Sym("unit"), 1]]]]])
    # titles
    for b, (bx, by) in BLOCKS.items():
        body.append([Sym("text"), TITLES[b], [Sym("exclude_from_sim"), Sym("no")], [Sym("at"), bx, by - 8, 0],
                     [Sym("effects"), [Sym("font"), [Sym("size"), 3, 3], [Sym("bold"), Sym("yes")]], [Sym("justify"), Sym("left")]],
                     [Sym("uuid"), uid("title", b)]])
    out.append([Sym("lib_symbols")] + list(libsyms.values()))
    out += body
    out.append([Sym("sheet_instances"), [Sym("path"), "/", [Sym("page"), "1"]]])
    out.append([Sym("embedded_fonts"), Sym("no")])
    return out


if __name__ == "__main__":
    open(OUT, "w").write(dump(build()) + "\n")
    print("wrote", OUT)
