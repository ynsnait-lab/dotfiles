# dotfiles — config du Mac de Younes

La config de mon terminal et la liste de mes paquets, pour tout retrouver en 5 minutes sur un nouveau Mac.

| Fichier | Rôle | Lien sur le Mac |
|---|---|---|
| `.zshrc` | alias et fonctions (`maj`, `brewsave`, `z`, `ll`, `gacp`, `esp`, `ports`…), prompt starship, fzf, zoxide | `~/.zshrc` |
| `.zprofile` | PATH Homebrew et Python au démarrage | `~/.zprofile` |
| `.gitconfig` | identité Git, diffs avec delta | `~/.gitconfig` |
| `Brewfile` | tous les paquets Homebrew, apps (casks), extensions VS Code, outils uv et npm | `~/Brewfile` |

Les fichiers du Mac sont des **liens symboliques** vers ce dossier : modifier `~/.zshrc`, c'est modifier `~/dotfiles/.zshrc`.

## Au quotidien

```sh
maj          # met tout à jour (Homebrew, outils uv, App Store si mas est installé)
brewsave     # réécrit le Brewfile avec ce qui est installé
cd ~/dotfiles && git add -A && git commit -m "maj config" && git push   # sauvegarder sur GitHub
```

## Sur un nouveau Mac

```sh
# 1. Homebrew : https://brew.sh
# 2. puis :
git clone https://github.com/ynsnait-lab/dotfiles.git ~/dotfiles
~/dotfiles/install.sh
```

`install.sh` met de côté les fichiers existants dans `~/.dotfiles-backup-<date>/`, crée les liens, puis réinstalle tout le Brewfile.

Le détail de chaque commande est dans la fiche « Power User Mac » (Bureau › Shortcuts).
