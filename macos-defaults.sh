#!/bin/zsh
# Réglages cachés macOS (appliqués le 01/10/2026). Relançable sans risque : ./macos-defaults.sh
# Annuler un réglage : defaults delete <domaine> <clé>  puis  killall Finder / killall Dock
# Valeurs d'avant : ShowPathbar=0, show-recents=1, mru-spaces=1, les autres absentes (défaut macOS).

# Finder : barre du chemin en bas, dossiers toujours en premier
defaults write com.apple.finder ShowPathbar -bool true
defaults write com.apple.finder _FXSortFoldersFirst -bool true

# Dock (masqué) : apparition instantanée, animation plus courte, pas d'apps récentes
defaults write com.apple.dock autohide-delay -float 0
defaults write com.apple.dock autohide-time-modifier -float 0.3
defaults write com.apple.dock show-recents -bool false

# Bureaux : gardent leur ordre (⌃1, ⌃2… tombent toujours au même endroit)
defaults write com.apple.dock mru-spaces -bool false

# Pas de fichiers .DS_Store sur les partages réseau ni sur les clés/disques USB
defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true
defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true

killall Finder Dock 2>/dev/null
echo "✅ Réglages appliqués."
