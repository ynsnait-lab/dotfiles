#!/bin/zsh
# Lancé chaque heure par launchd (fr.younes.rangeur) via /Applications/Rangeur.app.
# Le rangeur lui-même est le dépôt public github.com/ynsnait-lab/rangeur ; la config perso est ~/.rangeur/config.json.
print "=== $(date '+%F %T')"
exec /usr/bin/python3 "$HOME/Globale - Dossiers/04 — DEV & OUTILS/Dépôts GitHub/ynsnait-lab/rangeur/rangeur.py"
