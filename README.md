# dotfiles — config du Mac de Younes

La config de mon terminal et la liste de mes paquets, pour tout retrouver en 5 minutes sur un nouveau Mac.

| Fichier | Rôle | Lien sur le Mac |
|---|---|---|
| `.zshrc` | alias et fonctions (`maj`, `brewsave`, `z`, `ll`, `gacp`, `esp`, `ports`…), prompt starship, fzf, zoxide | `~/.zshrc` |
| `.zprofile` | PATH Homebrew et Python au démarrage | `~/.zprofile` |
| `.gitconfig` | identité Git, diffs avec delta | `~/.gitconfig` |
| `Brewfile` | tous les paquets Homebrew, apps (casks), extensions VS Code, outils uv et npm | `~/Brewfile` |
| `bin/` | `notif`, `range-capture`, `courrier-admin`, `ocr.swift` : les scripts appelés par le terminal et par les raccourcis | `~/dotfiles/bin` (dans le PATH) |
| `shortcuts/` | raccourcis signés « Ranger la capture » et « Courrier admin vers Rappel » (double-clic pour les ajouter) | app Raccourcis |
| `macos-defaults.sh` | réglages cachés macOS (Finder, Dock, bureaux, .DS_Store) — relançable | — |

Les fichiers du Mac sont des **liens symboliques** vers ce dossier : modifier `~/.zshrc`, c'est modifier `~/dotfiles/.zshrc`.

## Au quotidien

```sh
maj          # met tout à jour (Homebrew, outils uv, App Store si mas est installé)
brewsave     # réécrit le Brewfile avec ce qui est installé
cd ~/dotfiles && git add -A && git commit -m "maj config" && git push   # sauvegarder sur GitHub
```

## Automatisations

- **Fin de tâche** : toute commande de plus de 60 s envoie une notif (Mac, et iPhone si tu n'es pas devant). `fini <commande>` force la notif, `maj` en envoie une à la fin. Canal ntfy dans `~/.config/notif/topic` (hors Git).
- **Captures d'écran** : automatisation Raccourcis « capture enregistrée » → `range-capture` (Images › Captures › AAAA-MM, nom de l'app, texte cherchable avec Spotlight).
- **Courrier admin** : automatisation « notification de Mail » → `courrier-admin` (rappel « À traiter » dans TO-DO si ameli, CPAM, URSSAF, impôts, CAF…). Journal : `~/Library/Logs/courrier-admin.log`.

## Sur un nouveau Mac

```sh
# 1. Homebrew : https://brew.sh
# 2. puis :
git clone https://github.com/ynsnait-lab/dotfiles.git ~/dotfiles
~/dotfiles/install.sh
```

`install.sh` met de côté les fichiers existants dans `~/.dotfiles-backup-<date>/`, crée les liens, puis réinstalle tout le Brewfile. Lance ensuite `~/dotfiles/macos-defaults.sh` pour retrouver les réglages du Finder et du Dock.

Le détail de chaque commande est dans la fiche « Power User Mac » (Bureau › Shortcuts).
