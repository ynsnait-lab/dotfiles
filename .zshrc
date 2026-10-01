# 1. Moteur de complétion (Une seule fois suffit !)
autoload -Uz compinit && compinit

# 2. Environnement UV et Python
. "$HOME/.local/bin/env"
export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"

# 3. Raccourcis Personnels
# Tape "gacp 'ton message'" pour add, commit et push d'un coup
gacp() { git add . && git commit -m "$1" && git push; }

# Alias pour lancer l'IA avec approbation manuelle (SANS --auto_run)
alias oi='uvx --from open-interpreter --with "setuptools<70" interpreter --model ollama/Jarvis'

# 4. OpenClaw (À charger à la fin)
if [ -f "/Users/younesnait/.openclaw/completions/openclaw.zsh" ]; then
    source "/Users/younesnait/.openclaw/completions/openclaw.zsh"
fi
alias oi='uvx --python 3.12 --from open-interpreter interpreter --model ollama/Jarvis --os'
launchctl setenv OLLAMA_ORIGINS "*"
alias p="python3"
alias rf="ruff format ."
alias rc="ruff check --fix ."
alias spy="ipython"
alias mknote="python3 ~/Documents/scripts/make_note.py"

# ============================================================
#  Power-user CLI — ajoute le 2026-06-02 (sauvegarde dans ~/.dotfiles-backup-*)
#  Pour tout desactiver : supprime ce bloc et ouvre un nouveau terminal.
# ============================================================
eval "$(zoxide init zsh)"          # 'z <bout-de-chemin>' = cd intelligent (ex: z down -> ~/Downloads)
source <(fzf --zsh)                # Ctrl-R: historique flou | Ctrl-T: fichiers | Alt-C: dossiers
eval "$(starship init zsh)"        # prompt moderne (git, langage, duree des commandes...)

alias ll='eza -lah --git --group-directories-first'        # liste detaillee + statut git
alias la='eza -a --group-directories-first'                # tout, en grille
alias lt='eza --tree --level=2 --group-directories-first'  # arborescence sur 2 niveaux
# (ls et cat restent inchanges ; tape 'bat fichier' pour un cat colore, 'fd motif' pour chercher)

# ============================================================
#  Power-user v2 — ajoute le 2026-09-29 (copie avant modif : ~/.dotfiles-backup-20260929-zshrc)
#  Detail dans Bureau/Shortcuts/Power-User-Mac-Younes.pdf
#  Pour tout desactiver : supprime ce bloc et ouvre un nouveau terminal.
# ============================================================
export PATH="$PATH:$HOME/.platformio/penv/bin"                                        # 'pio' dispo partout
export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"   # 'code .' ouvre VS Code ici
export HOMEBREW_NO_ENV_HINTS=1                                                       # brew moins bavard

# maj : met TOUT a jour (Homebrew + outils uv + App Store si 'mas' est installe) et liste les MAJ macOS
maj() {
  echo "🍺 Homebrew…" && brew update && brew upgrade && brew autoremove && brew cleanup --prune=7
  command -v uv  >/dev/null && { echo "🐍 Outils uv…"; uv tool upgrade --all; }
  command -v mas >/dev/null && { echo "🛍  App Store…"; mas upgrade; }
  echo "🍎 macOS :"; softwareupdate --list 2>&1 | grep -E "Label|No new" || true
  echo "✅ Termine."
}
alias brewsave='brew bundle dump --force --file=$HOME/dotfiles/Brewfile'   # photo de tes paquets -> ~/dotfiles/Brewfile (lien ~/Brewfile)
alias ports='lsof -iTCP -sTCP:LISTEN -n -P'                                  # qui ecoute sur quel port
alias ipl='ipconfig getifaddr en0'                                           # IP locale (Wi-Fi)
alias ipp='curl -s https://ifconfig.me; echo'                                # IP publique
alias flushdns='sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder'  # vide le cache DNS
alias cafe='caffeinate -dims'                                                # Mac eveille tant que ca tourne (⌃C = stop)
alias esp='ls /dev/cu.* | grep -v -E "Bluetooth|debug"'                      # ports serie (ESP32, STM32…)
