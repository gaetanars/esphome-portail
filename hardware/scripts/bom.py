"""Write the PCBWay BOM (CSV) from design.py. Usage: bom.py out.csv"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design

L = "https://www.lcsc.com/product-detail/%s.html"
LINKS = {  # public distributor pages checked on 2026-11-11 (not PCBWay's own parts library)
    "GRM32ER71H106KA12L": L % "C77102", "CL21A106KAYNNNE": L % "C15850", "CL21A226MPQNNNE": L % "C29277",
    "CL10B105KA8NNNC": L % "C29936", "CC0603KRX7R9BB104": L % "C14663", "SS36": L % "C116712",
    "1N4148W-7-F": L % "C83528", "MF-MSMF020/60-2": L % "C719178", "DG500-5.08-03P-14-00A(H)": L % "C581322",
    "DG500-5.08-02P-14-00A(H)": L % "C691859", "TYPE-C-31-M-12": L % "C165948", "SRN6045TA-6R8M": L % "C2041457",
    "KT-0603G": L % "C12624", "KT-0603R": L % "C2286", "MMBT3904LT1G": L % "C81464", "AO3400A": L % "C20917",
    "SMBJ26CA": L % "C83332", "AP7361C-33E-13": L % "C500795", "USBLC6-2SC6": L % "C7519", "CH340C": L % "C84681",
    "ESP32-WROOM-32UE-N4": L % "C701344", "LTV-817S-TA1": L % "C125121", "TS-1187A-B-A-B": L % "C318884",
    "V275LA4P": L % "C129558", "SR2512MK-0751KL": L % "C2137725",
    "G5V-1-DC5": "https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/G5V-1-DC5/87831",
    "LMR16006YQDDCRQ1": "https://www.digikey.com/en/products/detail/texas-instruments/LMR16006YQDDCRQ1/5395816",
    "LTV-814S-TA1": "https://www.mouser.com/ProductDetail/Lite-On/LTV-814S-TA1",
}
rows = {}
for p in design.PARTS:
    if p.get("mech"):
        continue
    k = (p["value"], p["fp"].split(":")[1], p["mfr"], p["mpn"])
    rows.setdefault(k, []).append(p["ref"])
with open(sys.argv[1], "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Quantity", "Value", "Footprint", "Manufacturer", "Manufacturer Part Number", "Supplier link", "DNP"])
    for (val, fp, mfr, mpn), refs in sorted(rows.items(), key=lambda kv: kv[1][0]):
        w.writerow([",".join(refs), len(refs), val, fp, mfr, mpn, LINKS.get(mpn, ""), ""])
