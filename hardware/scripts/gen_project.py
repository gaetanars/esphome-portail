"""Generate .kicad_pro and library tables for portail-pcb."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import design

D = os.path.join(os.path.dirname(__file__), "..", "portail-pcb")
sl = sorted({p["sym"].split(":")[0] for p in design.PARTS} | {"power"})
fl = sorted({p["fp"].split(":")[0] for p in design.PARTS})
open(f"{D}/sym-lib-table", "w").write("(sym_lib_table\n\t(version 7)\n" + "".join(
    f'\t(lib (name "{n}")(type "KiCad")(uri "${{KICAD10_SYMBOL_DIR}}/{n}.kicad_sym")(options "")(descr ""))\n' for n in sl) + ")\n")
open(f"{D}/fp-lib-table", "w").write("(fp_lib_table\n\t(version 7)\n" + "".join(
    f'\t(lib (name "{n}")(type "KiCad")(uri "${{KICAD10_FOOTPRINT_DIR}}/{n}.pretty")(options "")(descr ""))\n' for n in fl) + ")\n")
pro = {"meta": {"filename": "portail-pcb.kicad_pro", "version": 3},
       "erc": {"rule_severities": {"pin_to_pin": "warning"}},
       "board": {"design_settings": {"rules": {}, "rule_severities": {
           "lib_footprint_mismatch": "ignore", "silk_edge_clearance": "ignore", "silk_over_copper": "ignore"}}},
       "net_settings": {"classes": [
           {"name": "Default", "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3},
           {"name": "Power", "clearance": 0.25, "track_width": 0.6, "via_diameter": 0.8, "via_drill": 0.4},
           {"name": "HV230", "clearance": 0.5, "track_width": 0.4, "via_diameter": 0.8, "via_drill": 0.4}],
           "meta": {"version": 4},
           "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in design.POWER_NETS] +
                                [{"netclass": "HV230", "pattern": n} for n in design.HV_NETS]},
       "sheets": [["7f0c2a4e-5b1d-4c3a-9e77-0a1b2c3d4e5f", "Root"]]}
json.dump(pro, open(f"{D}/portail-pcb.kicad_pro", "w"), indent=2)
print("ok")
