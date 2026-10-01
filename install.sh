#!/bin/zsh
# Installe ces dotfiles sur un Mac : sauvegarde les fichiers existants, crée les liens, réinstalle les paquets.
set -e
DIR="${0:A:h}"
BK="$HOME/.dotfiles-backup-$(date +%Y%m%d-%H%M%S)"

for f in .zshrc .zprofile .gitconfig Brewfile; do
  target="$HOME/$f"
  if [[ -e "$target" && ! -L "$target" ]]; then
    mkdir -p "$BK" && mv "$target" "$BK/"
    echo "sauvegardé : $target -> $BK/"
  fi
  ln -sfn "$DIR/$f" "$target"
  echo "lien : $target -> $DIR/$f"
done

if command -v brew >/dev/null; then
  brew bundle install --file="$DIR/Brewfile"
else
  echo "Homebrew absent : installe-le (https://brew.sh) puis relance ce script."
fi
echo "✅ Terminé — ouvre un nouveau terminal."
