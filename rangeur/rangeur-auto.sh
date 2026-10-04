#!/bin/zsh
# Lancé chaque heure par launchd (fr.younes.rangeur). Range ce qui attend depuis plus de 24 h.
# Sources : Téléchargements du Mac + téléchargements de l'iPhone/iPad arrivant dans iCloud Drive.
PY=/usr/bin/python3
RG="$HOME/dotfiles/rangeur/rangeur.py"
QI="$HOME/Documents/99 — Quarantaine (rien supprimé)/$(date +%Y-%m) — Rangeur"
IC="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
AU="$HOME/Documents/AUTRES/TÉLÉCHARGEMENTS/Téléchargement MacBook Pro"
print "=== $(date '+%F %T')"
$PY "$RG"
[[ -d "$IC" ]] && $PY "$RG" --source "$IC" --quarantaine "$QI" --journal-md "$HOME/Downloads"
[[ -d "$AU" ]] && $PY "$RG" --source "$AU" --quarantaine "$QI" --journal-md "$HOME/Downloads"
exit 0
