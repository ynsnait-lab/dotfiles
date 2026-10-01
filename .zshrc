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
  local t0=$EPOCHSECONDS n=0 rc=0
  echo "🍺 Homebrew…" && brew update && n=$(brew outdated --quiet | wc -l | tr -d ' ') \
    && brew upgrade && brew autoremove && brew cleanup --prune=7 || rc=$?
  command -v uv  >/dev/null && { echo "🐍 Outils uv…"; uv tool upgrade --all; }
  command -v mas >/dev/null && { echo "🛍  App Store…"; mas upgrade; }
  echo "🍎 macOS :"; local os=$(softwareupdate --list 2>&1 | grep -E "Label|No new"); echo "$os"
  echo "✅ Termine."
  local extra=""; [[ $os == *Label* ]] && extra=" · MAJ macOS dispo"
  if (( rc == 0 )); then notif -t "✅ maj terminée" -g white_check_mark "$n paquets Homebrew mis à jour en $(_duree $((EPOCHSECONDS - t0)))$extra"
  else notif -t "❌ maj : erreur Homebrew" -g x "Code $rc après $(_duree $((EPOCHSECONDS - t0))) — regarde le terminal"; fi
}
alias brewsave='brew bundle dump --force --file=$HOME/dotfiles/Brewfile'   # photo de tes paquets -> ~/dotfiles/Brewfile (lien ~/Brewfile)
alias ports='lsof -iTCP -sTCP:LISTEN -n -P'                                  # qui ecoute sur quel port
alias ipl='ipconfig getifaddr en0'                                           # IP locale (Wi-Fi)
alias ipp='curl -s https://ifconfig.me; echo'                                # IP publique
alias flushdns='sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder'  # vide le cache DNS
alias cafe='caffeinate -dims'                                                # Mac eveille tant que ca tourne (⌃C = stop)
alias esp='ls /dev/cu.* | grep -v -E "Bluetooth|debug"'                      # ports serie (ESP32, STM32…)

# ============================================================
#  Notifs de fin de tâche — ajouté le 2026-10-02 (scripts dans ~/dotfiles/bin)
#  notif "msg"      : notification Mac + iPhone (app ntfy)
#  fini <commande>  : lance la commande et te prévient à la fin, réussite ou échec
#  automatique      : toute commande de plus de $NOTIF_SEUIL s te prévient ; sur l'iPhone
#                     seulement si tu n'as pas touché le Mac depuis 60 s
# ============================================================
export PATH="$HOME/dotfiles/bin:$PATH"
zmodload zsh/datetime
autoload -Uz add-zsh-hook
NOTIF_SEUIL=60

_duree() { (( $1 >= 60 )) && echo "$(( $1 / 60 )) min $(( $1 % 60 )) s" || echo "$1 s"; }

fini() {
  local t0=$EPOCHSECONDS; "$@"; local rc=$?
  local d=$(_duree $(( EPOCHSECONDS - t0 )))
  if (( rc == 0 )); then notif -t "✅ Terminé" -g white_check_mark "$* ($d)"
  else notif -t "❌ Échec (code $rc)" -g x "$* ($d)"; fi
  return $rc
}

_notif_preexec() { _notif_cmd=$1; _notif_t0=$EPOCHSECONDS; }
_notif_precmd() {
  local rc=$?
  [[ -z ${_notif_t0:-} ]] && return
  local c=$_notif_cmd d=$(( EPOCHSECONDS - _notif_t0 ))
  unset _notif_cmd _notif_t0
  (( d < NOTIF_SEUIL )) && return
  case ${c%% *} in   # commandes interactives ou qui préviennent déjà : pas de notif
    fini|maj|btop|top|htop|ssh|vi|vim|nvim|nano|less|more|man|tail|watch|ipython|spy|oi|claude|codex|gemini|aider|cafe|caffeinate|lazygit|tmux|screen) return;;
  esac
  [[ $c == (python|python3|p) || $c == "pio device monitor"* || $c == "ollama run"* ]] && return
  if (( rc == 0 )); then notif -i -t "✅ Terminé" -g white_check_mark "$c ($(_duree $d))"
  else notif -i -t "❌ Échec (code $rc)" -g x "$c ($(_duree $d))"; fi
}
add-zsh-hook preexec _notif_preexec
precmd_functions=(_notif_precmd ${precmd_functions:#_notif_precmd})   # en premier, pour lire le bon code retour
