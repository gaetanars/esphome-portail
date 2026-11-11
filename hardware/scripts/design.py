"""Single source of truth for the portail PCB: components and connectivity.

Used by gen_sch.py (schematic), gen_pcb.py (board) and export.sh (BOM).
Pins are listed per component as {pin_number: net}. Pins not listed are
flagged "no connect" in the schematic and left without net on the board.
"""

GND = "GND"

# Each part: ref, lib "Lib:Symbol", value, footprint "Lib:Name", pins, block, mfr, mpn
# Optional: dnp, rot (schematic), note
PARTS = []


def P(ref, sym, value, fp, pins, block, mfr="", mpn="", **kw):
    PARTS.append(dict(ref=ref, sym=sym, value=value, fp=fp, pins=pins, block=block,
                      mfr=mfr, mpn=mpn, **kw))


R = "Device:R"
C = "Device:C"
R06 = "Resistor_SMD:R_0603_1608Metric"
C06 = "Capacitor_SMD:C_0603_1608Metric"
C08 = "Capacitor_SMD:C_0805_2012Metric"
LED06 = "LED_SMD:LED_0603_1608Metric"
SOD = "Diode_SMD:D_SOD-123"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
TB5 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-%d-5.08_1x%02d_P5.08mm_Horizontal"

# ---------------------------------------------------------------- POWER
P("J1", "Connector:Screw_Terminal_01x03", "J1 Alim/W.L.", TB5 % (3, 3),
  {"1": "+24V_IN", "2": GND, "3": "WL_IN"}, "power", "Degson", "DG500-5.08-03P-14-00A(H)")
P("F1", "Device:Polyfuse", "0.2A hold 1812", "Fuse:Fuse_1812_4532Metric",
  {"1": "+24V_IN", "2": "24V_F"}, "power", "Bourns", "MF-MSMF020/60-2")
P("TVS1", "Device:D_TVS", "SMBJ26CA", "Diode_SMD:D_SMB",
  {"1": "24V_F", "2": GND}, "power", "Littelfuse", "SMBJ26CA")
P("D1", "Device:D_Schottky", "SS36", "Diode_SMD:D_SMA",
  {"1": "VIN24", "2": "24V_F"}, "power", "Jingdao Microelectronics", "SS36")
P("C1", C, "10uF/50V", "Capacitor_SMD:C_1210_3225Metric",
  {"1": "VIN24", "2": GND}, "power", "Murata", "GRM32ER71H106KA12L")
P("C2", C, "10uF/50V", "Capacitor_SMD:C_1210_3225Metric",
  {"1": "VIN24", "2": GND}, "power", "Murata", "GRM32ER71H106KA12L")
P("R1", R, "100k", R06, {"1": "VIN24", "2": "BUCK_EN"}, "power", "Yageo", "RC0603FR-07100KL")
P("U1", "Regulator_Switching:LMR16006YQ", "LMR16006YQ", "Package_TO_SOT_SMD:SOT-23-6",
  {"1": "BUCK_CB", "2": GND, "3": "BUCK_FB", "4": "BUCK_EN", "5": "VIN24", "6": "BUCK_SW"},
  "power", "Texas Instruments", "LMR16006YQDDCRQ1")
P("CB1", C, "100nF", C06, {"1": "BUCK_CB", "2": "BUCK_SW"}, "power", "Yageo", "CC0603KRX7R9BB104")
P("D2", "Device:D_Schottky", "SS36", "Diode_SMD:D_SMA",
  {"1": "BUCK_SW", "2": GND}, "power", "Jingdao Microelectronics", "SS36")
P("L1", "Device:L", "6.8uH 1.6A", "Inductor_SMD:L_Bourns_SRN6045TA",
  {"1": "BUCK_SW", "2": "BUCK5"}, "power", "Bourns", "SRN6045TA-6R8M")
P("C3", C, "22uF/10V", C08, {"1": "BUCK5", "2": GND}, "power", "Samsung", "CL21A226MPQNNNE")
P("C4", C, "22uF/10V", C08, {"1": "BUCK5", "2": GND}, "power", "Samsung", "CL21A226MPQNNNE")
P("R2", R, "54.9k", R06, {"1": "BUCK5", "2": "BUCK_FB"}, "power", "Yageo", "RC0603FR-0754K9L")
P("R3", R, "10k", R06, {"1": "BUCK_FB", "2": GND}, "power", "Yageo", "RC0603FR-0710KL")
P("D3", "Device:D_Schottky", "SS36", "Diode_SMD:D_SMA",
  {"1": "+5V", "2": "BUCK5"}, "power", "Jingdao Microelectronics", "SS36")
P("D4", "Device:D_Schottky", "SS36", "Diode_SMD:D_SMA",
  {"1": "+5V", "2": "VBUS"}, "power", "Jingdao Microelectronics", "SS36")
P("C5", C, "22uF/10V", C08, {"1": "+5V", "2": GND}, "power", "Samsung", "CL21A226MPQNNNE")
P("U2", "Regulator_Linear:AP7361C-33E", "AP7361C-33E", "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
  {"1": "+5V", "2": GND, "3": "+3V3"}, "power", "Diodes Inc", "AP7361C-33E-13")
P("C6", C, "22uF/10V", C08, {"1": "+3V3", "2": GND}, "power", "Samsung", "CL21A226MPQNNNE")
P("C7", C, "100nF", C06, {"1": "+3V3", "2": GND}, "power", "Yageo", "CC0603KRX7R9BB104")
P("R4", R, "1k", R06, {"1": "+3V3", "2": "LED_PWR"}, "power", "Yageo", "RC0603FR-071KL")
P("LED1", "Device:LED", "vert", LED06, {"1": GND, "2": "LED_PWR"}, "power", "Hubei KENTO", "KT-0603G")

# ---------------------------------------------------------------- USB
P("J4", "Connector:USB_C_Receptacle_USB2.0_16P", "USB-C", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
  {"A1": GND, "B1": GND, "A12": GND, "B12": GND, "SH": GND,
   "A4": "VBUS", "B4": "VBUS", "A9": "VBUS", "B9": "VBUS",
   "A5": "CC1", "B5": "CC2", "A6": "USB_DP", "B6": "USB_DP", "A7": "USB_DM", "B7": "USB_DM"},
  "usb", "Korean Hroparts", "TYPE-C-31-M-12")
P("R5", R, "5.1k", R06, {"1": "CC1", "2": GND}, "usb", "Yageo", "RC0603FR-075K1L")
P("R6", R, "5.1k", R06, {"1": "CC2", "2": GND}, "usb", "Yageo", "RC0603FR-075K1L")
P("U3", "Power_Protection:USBLC6-2SC6", "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6",
  {"1": "USB_DP", "6": "USB_DP", "3": "USB_DM", "4": "USB_DM", "2": GND, "5": "VBUS"},
  "usb", "STMicroelectronics", "USBLC6-2SC6")
P("U4", "Interface_USB:CH340C", "CH340C", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm",
  {"1": GND, "2": "CH_TXD", "3": "CH_RXD", "4": "+3V3", "5": "USB_DP", "6": "USB_DM",
   "13": "DTR_N", "14": "RTS_N", "16": "+3V3"},
  "usb", "WCH", "CH340C")
P("C8", C, "100nF", C06, {"1": "+3V3", "2": GND}, "usb", "Yageo", "CC0603KRX7R9BB104")
P("Q1", "Transistor_BJT:Q_NPN_BEC", "MMBT3904", SOT23, {"1": "Q1_B", "2": "RTS_N", "3": "ESP_EN"},
  "usb", "onsemi", "MMBT3904LT1G")
P("Q2", "Transistor_BJT:Q_NPN_BEC", "MMBT3904", SOT23, {"1": "Q2_B", "2": "DTR_N", "3": "ESP_IO0"},
  "usb", "onsemi", "MMBT3904LT1G")
P("R7", R, "10k", R06, {"1": "DTR_N", "2": "Q1_B"}, "usb", "Yageo", "RC0603FR-0710KL")
P("R8", R, "10k", R06, {"1": "RTS_N", "2": "Q2_B"}, "usb", "Yageo", "RC0603FR-0710KL")

# ---------------------------------------------------------------- ESP32
P("U5", "RF_Module:ESP32-WROOM-32UE", "ESP32-WROOM-32UE-N4", "RF_Module:ESP32-WROOM-32UE",
  {"1": GND, "15": GND, "38": GND, "39": GND, "2": "+3V3", "3": "ESP_EN", "25": "ESP_IO0",
   "34": "CH_TXD", "35": "CH_RXD",
   "27": "RELAY_A_G", "28": "RELAY_B_G", "10": "WL_SENSE", "11": "LAMP_SENSE"},
  "esp", "Espressif", "ESP32-WROOM-32UE-N4")
P("R9", R, "10k", R06, {"1": "+3V3", "2": "ESP_EN"}, "esp", "Yageo", "RC0603FR-0710KL")
P("C9", C, "1uF", C06, {"1": "ESP_EN", "2": GND}, "esp", "Samsung", "CL10B105KA8NNNC")
P("C10", C, "10uF", C08, {"1": "+3V3", "2": GND}, "esp", "Samsung", "CL21A106KAYNNNE")
P("C11", C, "100nF", C06, {"1": "+3V3", "2": GND}, "esp", "Yageo", "CC0603KRX7R9BB104")
P("SW1", "Switch:SW_Push", "RESET", "Button_Switch_SMD:SW_SPST_TL3342", {"1": "ESP_EN", "2": GND},
  "esp", "XKB", "TS-1187A-B-A-B")
P("SW2", "Switch:SW_Push", "BOOT", "Button_Switch_SMD:SW_SPST_TL3342", {"1": "ESP_IO0", "2": GND},
  "esp", "XKB", "TS-1187A-B-A-B")

# ---------------------------------------------------------------- RELAYS
for k, (rl, q, rg, d, rled, led, drain, gate, op, kn) in {
        "A": ("K1", "Q3", "R10", "D5", "R11", "LED2", "RELAY_A_D", "RELAY_A_G", "OP_A_T", 1),
        "B": ("K2", "Q4", "R12", "D6", "R13", "LED3", "RELAY_B_D", "RELAY_B_G", "OP_B_T", 2)}.items():
    P(q, "Transistor_FET:AO3400A", "AO3400A", SOT23, {"1": gate, "2": GND, "3": drain},
      "relay", "Alpha & Omega", "AO3400A")
    P(rg, R, "10k", R06, {"1": gate, "2": GND}, "relay", "Yageo", "RC0603FR-0710KL")
    P(rl, "Relay:G5V-1", "G5V-1-DC5", "Relay_THT:Relay_SPDT_Omron_G5V-1",
      {"2": "+5V", "9": drain, "5": "COM_T", "6": "COM_T", "10": op},
      "relay", "Omron", "G5V-1-DC5")
    P(d, "Device:D", "1N4148W", SOD, {"1": "+5V", "2": drain}, "relay", "Diodes Inc", "1N4148W-7-F")
    P(rled, R, "1k", R06, {"1": "+5V", "2": "LED_" + k}, "relay", "Yageo", "RC0603FR-071KL")
    P(led, "Device:LED", "red", LED06, {"1": drain, "2": "LED_" + k}, "relay", "Hubei KENTO", "KT-0603R")
P("J2", "Connector:Screw_Terminal_01x03", "J2 Commandes", TB5 % (3, 3),
  {"1": "OP_A_T", "2": "OP_B_T", "3": "COM_T"}, "relay", "Degson", "DG500-5.08-03P-14-00A(H)")

# ---------------------------------------------------------------- W.L. (24 V DC)
P("R14", R, "4.7k", R06, {"1": "WL_IN", "2": "WL_K"}, "wl", "Yageo", "RC0603FR-074K7L")
P("U6", "Isolator:EL817", "LTV-817S", "Package_DIP:SMDIP-4_W9.53mm",
  {"1": "VIN24", "2": "WL_K", "3": GND, "4": "WL_SENSE"}, "wl", "Lite-On", "LTV-817S-TA1")
P("D7", "Device:D", "1N4148W", SOD, {"1": "VIN24", "2": "WL_K"}, "wl", "Diodes Inc", "1N4148W-7-F")
P("R15", R, "10k", R06, {"1": "+3V3", "2": "WL_SENSE"}, "wl", "Yageo", "RC0603FR-0710KL")

# ---------------------------------------------------------------- LAMP (230 V~)
P("J3", "Connector:Screw_Terminal_01x02", "J3 LAMP 230V~", TB5 % (2, 2),
  {"1": "LAMP_L", "2": "LAMP_N"}, "lamp", "Degson", "DG500-5.08-02P-14-00A(H)")
P("RV1", "Device:Varistor", "275VAC 7mm", "Varistor:RV_Disc_D7mm_W3.4mm_P5mm",
  {"1": "LAMP_L", "2": "LAMP_N"}, "lamp", "Littelfuse", "V275LA4P")
P("R16", R, "51k 1W 2512 surge", "Resistor_SMD:R_2512_6332Metric", {"1": "LAMP_A", "2": "LAMP_M"},
  "lamp", "Yageo", "SR2512MK-0751KL")
P("R17", R, "51k 1W 2512 surge", "Resistor_SMD:R_2512_6332Metric", {"1": "LAMP_L", "2": "LAMP_M"},
  "lamp", "Yageo", "SR2512MK-0751KL")
P("U7", "Isolator:LTV-814", "LTV-814S", "Package_DIP:SMDIP-4_W9.53mm",
  {"1": "LAMP_N", "2": "LAMP_A", "3": GND, "4": "LAMP_SENSE"}, "lamp", "Lite-On", "LTV-814S-TA1")
P("R18", R, "10k", R06, {"1": "+3V3", "2": "LAMP_SENSE"}, "lamp", "Yageo", "RC0603FR-0710KL")

for i in range(1, 5):
    P(f"H{i}", "Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3",
      {}, "power", "", "", mech=True)

# Nets that must carry a PWR_FLAG (driven only by passive pins) : net -> part ref where the flag is attached
PWR_FLAGS = {GND: "J1", "+24V_IN": "J1", "VBUS": "J4", "+5V": "D3", "VIN24": "D1"}

# Net classes: widths in mm
POWER_NETS = ["+24V_IN", "24V_F", "VIN24", "BUCK_SW", "BUCK5", "+5V"]
HV_NETS = ["LAMP_L", "LAMP_N", "LAMP_M", "LAMP_A"]
