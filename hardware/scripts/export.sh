#!/bin/sh
# Produce the PCBWay files in hardware/production/ (ignored by git).
set -e
cd "$(dirname "$0")/.."
PCB=portail-pcb/portail-pcb.kicad_pcb
OUT=production
rm -rf "$OUT"; mkdir -p "$OUT/gerber"
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts \
  --no-x2 --subtract-soldermask -o "$OUT/gerber/" "$PCB" >/dev/null 2>&1
kicad-cli pcb export drill --format excellon --excellon-separate-th --drill-origin absolute \
  --excellon-units mm -o "$OUT/gerber/" "$PCB" >/dev/null 2>&1
(cd "$OUT/gerber" && zip -q ../portail-gerber.zip ./*)
kicad-cli pcb export pos --format csv --units mm --side front --smd-only -o "$OUT/portail-pos.csv" "$PCB" >/dev/null 2>&1
python3 scripts/bom.py "$OUT/portail-bom.csv"
unzip -l "$OUT/portail-gerber.zip" | tail -n +4
ls -l "$OUT"
