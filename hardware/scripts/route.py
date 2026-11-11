"""Export DSN, run Freerouting (jar given as argv[1]), import SES. Run with kpy.sh."""
import os, subprocess, sys
import pcbnew

JAVA = "/opt/homebrew/opt/openjdk/bin/java"
HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(HERE, "..", "portail-pcb", "portail-pcb.kicad_pcb")
jar = sys.argv[1]
work = sys.argv[2] if len(sys.argv) > 2 else "/tmp/portail-route"
os.makedirs(work, exist_ok=True)
dsn, ses = f"{work}/board.dsn", f"{work}/board.ses"

b = pcbnew.LoadBoard(PCB)
# drop any previous routing so the run is reproducible
for t in list(b.GetTracks()):
    b.Remove(t)
pcbnew.ExportSpecctraDSN(b, dsn)
subprocess.run([JAVA, "-jar", jar, "-de", dsn, "-do", ses, "-mp", "40", "-mt", "4",
                "--gui.enabled=false", "--usage_and_diagnostic_data.disable_analytics=true"],
               check=True, timeout=1500)
pcbnew.ImportSpecctraSES(b, ses)
b.Save(PCB)
print("routed; tracks:", len(b.GetTracks()))
