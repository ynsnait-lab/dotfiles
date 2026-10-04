# Rangeur

Garde `~/Downloads` propre sans jamais rien supprimer.

- Un fichier reste **24 h** dans Téléchargements, puis il est rangé selon les règles de `rangeur.py`.
- Ce qui est ambigu part dans `~/Documents/00 — À trier (ambigus)`.
- Doublons exacts et installeurs vont en quarantaine (jamais effacés).
- Journal lisible, toujours présent : `~/Downloads/_OÙ SONT MES FICHIERS.md`.
- Journal technique (annulation) : `~/.rangeur/journal.tsv`.

Sources surveillées : Téléchargements du Mac, `iCloud Drive/Downloads` (iPhone/iPad) et
`Documents/AUTRES/TÉLÉCHARGEMENTS/Téléchargement MacBook Pro`.

## Règles personnelles

Les règles qui contiennent des infos perso (plaque, numéros de devis, démarches…) ne sont pas dans ce dépôt :
elles vivent dans `~/.rangeur/regles-perso.json` (liste de `[clé, expression]`) et passent avant les règles générales.

## Commandes

```bash
python3 ~/dotfiles/rangeur/rangeur.py --plan                 # ce qui serait fait
python3 ~/dotfiles/rangeur/rangeur.py                        # rangement maintenant
python3 ~/dotfiles/rangeur/rangeur.py --annuler 2026-10-05   # remet en place une journée
```

## Automatisation

`fr.younes.rangeur.plist` (copié dans `~/Library/LaunchAgents`) lance `/Applications/Rangeur.app`
toutes les heures. L'app (source : `app/lanceur.c`) est la seule à recevoir l'accès complet au disque ;
elle lance `rangeur-auto.sh`.

Recompiler l'app : `clang -O2 -o /Applications/Rangeur.app/Contents/MacOS/Rangeur app/lanceur.c && codesign --force --sign - --identifier fr.younes.rangeur /Applications/Rangeur.app`
