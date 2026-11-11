# Carte ESP32 pour portail FAAC E045S

Carte 2 couches (108 × 80 mm, FR4 1,6 mm, ENIG), composants sur la face supérieure, assemblage complet PCBWay.
Brochage identique à `portail.yaml` : relais GPIO16/17 (actifs à l'état haut), W.L. GPIO25 et LAMP GPIO26 (actifs à l'état bas).

> **État : prototype non fabriqué, non testé.** ERC/DRC passent, mais aucune simulation ni essai physique.

## Vérification du BOM (11/11/2026)

Contrôle sur pages publiques de distributeurs (LCSC, DigiKey, Mouser, Arrow), liens dans `portail-bom.csv`. **Le stock de la
bibliothèque PCBWay elle-même n'est pas interrogeable sans compte** : à confirmer dans l'outil de devis PCBWay (les parts
absentes de leur stock sont sourcées chez eux ou à fournir en consignation).

Remplacements faits après contrôle : bornier Degson DG128-5.0 (pas **5,00** mm) → DG500-5.08 ; EL817S (rupture LCSC) → LTV-817S ;
LED Everlight 19-217 (arrêtée) → Hubei KENTO KT-0603 ; 10 µF/50 V Samsung (brokers seulement) → Murata ; RC2512 (aucun stock
fiable) → Yageo SR2512 (±20 %, 200 V de service chacune) ; SS26/SS14 unifiées en SS36.

Points de vigilance : PTC MF-MSMF020/60-2 « Not For New Designs » chez DigiKey (stock OK ailleurs) ; SMBJ26CA peu de stock LCSC ;
C9 (CL10B105KA8NNNC) volatil, tout 1 µF X7R ≥ 10 V en 0603 convient ; empreinte des borniers = Phoenix MKDS 5,08 générique,
**à confronter à la datasheet Degson DG500** (perçage, encombrement). Non contrôlés un par un : résistances/condensateurs Yageo 0603.

## Raccordement (pas 5,08 mm)

| Bornier | Broches | Vers FAAC |
|---|---|---|
| J1 | +24V / GND / W.L. | J9-17 / J9-15 / J11-20 |
| J2 | OP-A / OP-B / COM | J3-9 / J3-10 / J9-16 |
| J3 (230 V~) | L / N | J2-7 / J2-8 |

Alimentation : 24 V de J9 (500 mA max pour tous les accessoires). Fusible PTC 0,2 A sur la carte.

## Choix de conception à connaître

- Buck **LMR16006Y** (4–40 V, 0,6 A) : asynchrone, d'où la diode de roue libre D2. Schéma de référence TI (54,9 k / 10 k pour 5 V).
- TVS SMBJ26CA : écrête vers ~42 V, sous le maximum absolu du buck (65 V) mais au-dessus de sa plage de service (40 V).
- 5 V = buck OU VBUS USB (diodes Schottky) : flash possible sans 24 V. CH340C alimenté en 3,3 V (V3 relié à VCC) ; ERC signale
  ce raccordement en avertissement (`pin_to_pin`), c'est voulu.
- LAMP : 2 × 51 k (2512) en série → ~3 mA crête dans l'opto AC LTV-814 ; l'ondulation 50 Hz est filtrée par `lamp_off_delay`.
- Isolation 230 V : fente fraisée sous l'opto, 6 mm mini entre le net `HV230` et le reste (règle `.kicad_dru`), pas de cuivre de
  masse dans la zone. **Aucune certification** : à valider avant usage sur secteur.
- Relais : contacts secs entre OP-A/OP-B et COM.

## Régénérer / exporter

Prérequis : KiCad 10, openjdk, et le `.jar` Freerouting (release GitHub officielle) placé hors du dépôt.

```sh
hardware/scripts/build.sh /chemin/vers/freerouting.jar   # schéma + placement + routage + zones
hardware/scripts/export.sh                                 # Gerbers, perçages, placement, BOM -> hardware/production/
hardware/scripts/render.sh                                 # rendus PNG/SVG pour relecture
```

Source unique : `scripts/design.py` (composants, nets), `scripts/place.py` (placement).

## Commande PCBWay

1. PCB : uploader `production/portail-gerber.zip` ; 2 couches, 108 × 80 mm, 1,6 mm, finition ENIG, vernis vert, sérigraphie
   blanche. Vérifier la fente fraisée (couche Edge.Cuts) dans la visionneuse. Option conseillée : vernis de tropicalisation.
2. Assemblage : « Turnkey », face supérieure ; uploader `production/portail-bom.csv` et `production/portail-pos.csv`
   (coordonnées en mm ; Y négatif = convention KiCad, à valider dans l'aperçu PCBWay).
3. **Antenne non soudée** : commander à part un pigtail U.FL → SMA traversée de boîtier et une antenne 2,4 GHz 3–5 dBi.
4. Les relais, borniers, varistance et optos traversants/CMS sont assemblés par PCBWay (vérifier la disponibilité de chaque MPN).

## Premier essai (sans flasher depuis l'outil)

1. Contrôle visuel, puis mesure de continuité GND / 24 V / 5 V / 3,3 V à l'ohmmètre.
2. Mise sous tension **24 V seul** (sans 230 V, sans W.L.) : 5 V puis 3,3 V attendus, LED verte allumée.
3. Premier flash par USB-C (BOOT/RESET manuels si l'auto-reset échoue), puis raccordement W.L., commandes, et en dernier 230 V.
