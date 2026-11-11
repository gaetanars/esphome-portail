#!/bin/sh
# Render top view PNG + SVG of the board for visual review (output in /tmp/portail-render)
set -e
D="$(cd "$(dirname "$0")/../portail-pcb" && pwd)"; O=${1:-/tmp/portail-render}; mkdir -p "$O"
kicad-cli pcb render --side top --width 2000 --height 1600 -o "$O/top.png" "$D/portail-pcb.kicad_pcb" 2>&1 >/dev/null 2>&1 || true
kicad-cli pcb render --side bottom --width 2000 --height 1600 -o "$O/bottom.png" "$D/portail-pcb.kicad_pcb" 2>&1 >/dev/null 2>&1 || true
kicad-cli pcb export svg --layers "F.Cu,B.Cu,F.Silkscreen,Edge.Cuts,F.Fab" --mode-single --page-size-mode 2 -o "$O/layers.svg" "$D/portail-pcb.kicad_pcb" 2>&1 >/dev/null 2>&1 || true
