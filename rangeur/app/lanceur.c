/* Lanceur du rangeur : c'est cette app qui reçoit l'accès complet au disque,
   et le script qu'elle lance en hérite. Rien d'autre n'obtient cet accès. */
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
extern char **environ;
int main(void) {
    const char *home = getenv("HOME");
    char script[1024];
    if (!home) return 1;
    snprintf(script, sizeof script, "%s/dotfiles/rangeur/rangeur-auto.sh", home);
    char *argv[] = {"/bin/zsh", script, NULL};
    pid_t pid; int st = 0;
    if (posix_spawn(&pid, "/bin/zsh", NULL, NULL, argv, environ) != 0) return 1;
    waitpid(pid, &st, 0);
    return WIFEXITED(st) ? WEXITSTATUS(st) : 1;
}
