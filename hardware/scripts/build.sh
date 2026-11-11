#!/bin/sh
# Rebuild the whole design: schematic, project, board, routing (Freerouting), finishing.
# Usage: build.sh [path/to/freerouting.jar]   (jar kept outside the repo)
set -e
set -o pipefail 2>/dev/null || true
cd "$(dirname "$0")"
JAR=${1:-/tmp/freerouting-dl/freerouting-2.5.0.jar}
python3 gen_sch.py
./kpy.sh gen_project.py
./kpy.sh gen_pcb.py 2>&1 | grep -v assert || true
./kpy.sh route.py "$JAR" 2>&1 | grep -v assert | grep -A12 -E "could not be routed|^routed" || true
./kpy.sh finish.py 2>&1 | grep -v assert || true
