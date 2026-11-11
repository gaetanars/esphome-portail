# esphome-portail

Pilotage d'un portail battant **FAAC E045S** avec un ESP32 sous [ESPHome](https://esphome.io) : commande
ouvrir / fermer / stop / ouverture piéton, et retour d'état et de position dans Home Assistant, y compris pour les
mouvements déclenchés par la télécommande ou un bouton.

> ⚠️ **Sécurité** : la carte et la sortie LAMP sont en **230 V~**. Coupez l'alimentation avant toute intervention
> et faites intervenir une personne qualifiée. Un portail motorisé est une machine dangereuse : vérifiez le
> fonctionnement des sécurités (cellules, détection d'obstacle) après toute modification.

## Matériel

- ESP32 de type WROOM / `esp32dev` (GPIO16/17 sont indisponibles sur les modules WROVER à PSRAM).
- 2 relais (contact NO) : simulent les entrées OP-A et OP-B.
- 1 optocoupleur compatible 24 V : lit la sortie W.L.
- 1 module de détection 230 V (isolé) : lit la sortie LAMP.

### Exemples de références

Exemples non exhaustifs, à vérifier (tension, brochage, logique) avant achat : aucun n'est imposé.

| Rôle | Exemples |
|---|---|
| ESP32 | Espressif ESP32-DevKitC-32E (module WROOM-32E), ESP32 DevKit V1 (DOIT) – tout module WROOM sur carte `esp32dev` |
| Relais OP-A / OP-B | Module 2 relais 5 V à optocoupleur (relais SRD-05VDC-SL-C, contact NO) ; ou relais miniature 5 V + transistor |
| Lecture W.L. (24 V) | Module optocoupleur PC817 / EL817 (entrée 3,6–30 V, sortie collecteur vers GPIO) |
| Lecture LAMP (230 V~) | Module de détection tension secteur à optocoupleur (« AC 220 V optocoupler isolation board », sortie 3,3–5 V) ; ou relais miniature à bobine 230 V~ (famille Finder 40.31) dont le contact NO est lu par le GPIO |
| Alimentation ESP32 | Depuis la sortie 24 V de la carte (J9 – 17/18) via un convertisseur abaisseur 24 V → 5 V (MP1584, LM2596) ; ou module secteur isolé Hi-Link HLK-PM01 (5 V) |

Points d'attention :

- Beaucoup de modules relais sont **actifs à l'état bas** : vérifier la fiche et ajouter `inverted: true` sur les `switch` si besoin.
- Les modules d'entrée doivent être **isolés galvaniquement** (optocoupleur) ; ne jamais relier le 230 V ni le 24 V directement à un GPIO.
- Les capteurs analogiques de tension (type ZMPT101B) ne conviennent pas : il faut une sortie logique tout ou rien.
- Si la sortie du module est active à l'état haut, adapter `inverted` sur les `binary_sensor` `wl` et `lamp`.

## Câblage

Notice FAAC E045S, réf. 532373 Rev.A, FW 4.0 (non redistribuée : copyright FAAC, `docs/*.pdf` est ignoré par git).

| Fonction | Borne carte | Côté ESP32 | GPIO |
|---|---|---|---|
| OP-A (ouverture totale) | J3 – 9 | relais A, NO | GPIO16 |
| OP-B (ouverture piéton) | J3 – 10 | relais B, NO | GPIO17 |
| Commun « - » des commandes | J9 – 15/16 | commun des relais | – |
| W.L. (collecteur ouvert, 24 V 3 W, 100 mA max) | J11 – 20 | optocoupleur (+24 V : J9 – 17/18) | GPIO25 |
| LAMP (230 V~ 60 W) | J2 – 7/8 | module de détection 230 V | GPIO26 |

Les broches se changent via les `substitutions` de `portail.yaml`.

## Carte dédiée (optionnel)

`hardware/` contient une carte unique (KiCad 10) qui remplace les modules du commerce : ESP32-WROOM-32UE (antenne
déportée), 2 relais, optos W.L. et LAMP, alimentation 24 V → 5 V → 3,3 V et USB-C pour le premier flash. Le brochage
reste celui de `portail.yaml` (GPIO16/17/25/26) : aucun changement de firmware. Voir `hardware/README.md`.

## Réglages requis sur la carte

| Paramètre | Valeur | Raison |
|---|---|---|
| `Lo` (logique) | `E` ou `EP` | Seules logiques supportées (OPEN stoppe/inverse). `A`/`AP`/`SP` : fermeture auto non pilotée ; `b`/`C` : non supportées. |
| `Sp` (sortie W.L.) | `00` (défaut) | Fixe = ouverture/ouvert/pause, clignotante = fermeture, éteinte = fermé. |
| `PF` (préclignotement) | `no` de préférence | Évite un décalage entre commande et mouvement. |
| `tA` | indifférent | Absorbé par le calibrage des durées. |

## Principe de lecture d'état

- **LAMP** active = le portail bouge.
- **W.L.** donne le sens : fixe = ouverture, clignotante = fermeture, éteinte (à l'arrêt) = fermé.
- La position est intégrée dans le temps à partir des mouvements observés, et recalée à 0 % à chaque fermeture.
- Les commandes sont en boucle fermée : impulsion, observation du sens réel, correction si nécessaire.

## Entités exposées

- `cover` Portail (ouvrir / fermer / stop, position), bouton **Ouverture piéton**, capteur texte **État**.
- Diagnostic : **Durée dernier mouvement**, **Signal Wi-Fi**, **Uptime**, **Statut**, bouton **Redémarrer**.

## Calibrage des durées

Effectuer une course complète (totale, puis piéton) et lire le capteur **Durée dernier mouvement**, puis reporter
les valeurs dans les substitutions `open_time_total`, `close_time_total`, `open_time_partial`, `close_time_partial`.

## Installation

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp secrets.yaml.example secrets.yaml   # puis renseigner les vraies valeurs
.venv/bin/esphome config portail.yaml  # validation
.venv/bin/esphome run portail.yaml     # compile + flash (premier flash en USB)
```

Clé API : `openssl rand -base64 32`. Les valeurs de `secrets.yaml.example` sont factices (utilisées par la CI).

## Limites connues

- `has_position: true` sans `position_action` : le curseur de position de Home Assistant n'agit que sur 0 % / 100 %.
- La position est estimée (temps), pas mesurée : elle se recale uniquement à la fermeture.
- En mode piéton (2 moteurs), seul le vantail M1 s'ouvre : affiché à 50 %.

## Développement

```sh
pre-commit install
pre-commit run --all-files
```

La CI (GitHub Actions) lance le lint, `esphome config` et `esphome compile`.
