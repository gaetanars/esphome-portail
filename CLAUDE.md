# CLAUDE.md

## Contexte
Configuration ESPHome (`portail.yaml`) pour piloter un portail FAAC E045S depuis un ESP32 : 2 relais vers OP-A/OP-B,
retour d'état par W.L. (sens) et LAMP (mouvement). Voir `README.md` pour le câblage et les réglages carte.

## Commandes
Environnement : `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` (version ESPHome figée dans
`requirements.txt`, montée par Dependabot).

- Valider : `cp secrets.yaml.example secrets.yaml && .venv/bin/esphome config portail.yaml`
- Compiler (valide les lambdas C++) : `.venv/bin/esphome compile portail.yaml`
- Lint : `pre-commit run --all-files`

## Conventions
- Réglages dans `substitutions` ; commentaires en français ; identifiants et code en anglais.
- Commits : Conventional Commits (`type(scope): description`, impératif, anglais).
- `!secret` pour tout secret ; `secrets.yaml.example` ne contient que des valeurs factices.
- `docs/*.pdf` (notice FAAC) ne doit jamais être commité.

## Règles
- Ne jamais lire ni écrire de vrais secrets dans le code, les logs ou les commits.
- **Ne jamais flasher** (`esphome run|upload`) ni suivre les logs sans accord explicite : action physique sur un portail.
- Valider (`config`, `compile`, `pre-commit`) avant tout commit. Ne commit/push que sur demande.
