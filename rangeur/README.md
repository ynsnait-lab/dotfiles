# Rangeur — installation sur ce Mac

Le rangeur est un projet à part, public : **https://github.com/ynsnait-lab/rangeur**
(clone local : `~/Globale - Dossiers/04 — DEV & OUTILS/Dépôts GitHub/ynsnait-lab/rangeur`).

Ce dossier ne garde que ce qui est propre à ce Mac :

- `rangeur-auto.sh` : lancé chaque heure par `/Applications/Rangeur.app` (agent `fr.younes.rangeur`) ;
  il exécute le rangeur du dépôt public.
- `fr.younes.rangeur.plist` : l'agent launchd (copié dans `~/Library/LaunchAgents`).
- `app/lanceur.c` : source de `/Applications/Rangeur.app` (celle qui a l'accès complet au disque).
  Ne pas recompiler sans raison : l'autorisation macOS serait à redonner.

La config perso (destinations, règles, dont les règles privées) est dans `~/.rangeur/config.json`, hors Git.
Ne pas lancer `installer.sh` du dépôt public sur ce Mac : tout est déjà installé.
