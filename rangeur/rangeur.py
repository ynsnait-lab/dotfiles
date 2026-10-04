#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rangeur — garde ~/Downloads propre, sans jamais rien supprimer.

- Un élément reste 24 h dans Téléchargements, puis il est rangé selon les règles ci-dessous.
- Ce qui est ambigu part dans ~/Documents/00 — À trier (ambigus).
- Un doublon exact (même empreinte SHA-256) et les installeurs partent en quarantaine.
- Chaque déplacement est noté dans ~/Downloads/_OÙ SONT MES FICHIERS.md
  et dans ~/.rangeur/journal.tsv (qui permet d'annuler).

Commandes
  python3 rangeur.py                        rangement normal
  python3 rangeur.py --plan                 montre ce qui serait fait, sans rien bouger
  python3 rangeur.py --annuler 2026-10-05   remet en place ce qui a été rangé ce jour-là
"""
import argparse, datetime, errno, fcntl, hashlib, json, os, re, shutil, subprocess, sys, time, unicodedata, zipfile

HOME = os.path.expanduser("~")
DOCS = os.path.join(HOME, "Documents")
ACT = os.path.join(DOCS, "01 — Actif (cloud)")
ARC = os.path.join(DOCS, "02 — Archive")
AMB = os.path.join(DOCS, "00 — À trier (ambigus)")
GL = os.path.join(HOME, "Globale - Dossiers")
NPS = os.path.join(GL, "05 — ENTREPRENEURIAT", "Nait Pool Services")
DL = os.path.join(HOME, "Downloads")
QL = os.path.join(GL, "99 — Archives & Quarantaine", "Quarantaine — à supprimer")
STATE = os.path.join(HOME, ".rangeur")
JOURNAL_TSV = os.path.join(STATE, "journal.tsv")
JOURNAL_MD = "_OÙ SONT MES FICHIERS.md"
CALIBREDB = "/Applications/calibre.app/Contents/MacOS/calibredb"
CALIBRE_LIB = os.path.join(HOME, "Bibliothèque calibre")
SF_DATALESS = 0x40000000

DEST = {
    "litiges": os.path.join(ACT, "Démarches & litiges"),
    "nps_site": os.path.join(NPS, "01 — Site web", "Rapports DMARC"),
    "nps_carte": os.path.join(NPS, "02 — Identité", "carte-de-visite"),
    "nps_flyer": os.path.join(NPS, "02 — Identité", "flyers"),
    "nps_logo": os.path.join(NPS, "02 — Identité", "logo"),
    "nps": os.path.join(NPS, "04 — Administratif"),
    "paie": os.path.join(ACT, "Finances & impôts", "Paie", "ESRF"),
    "impots": os.path.join(ACT, "Finances & impôts", "IMPOTS"),
    "immobilier": os.path.join(ACT, "Finances & impôts", "IMMOBILIER"),
    "finances": os.path.join(ACT, "Finances & impôts"),
    "sante_examen": os.path.join(ACT, "Santé", "EXAMENS"),
    "sante_arret": os.path.join(ACT, "Santé", "ATTESTATIONS"),
    "sante": os.path.join(ACT, "Santé", "AUTRES"),
    "logement": os.path.join(ACT, "Logement & domicile"),
    "vehicule": os.path.join(ACT, "Véhicules & permis", "Véhicules"),
    "identite": os.path.join(ACT, "Identité & papiers"),
    "scolarite": os.path.join(ACT, "Diplômes & relevés", "Certificats de scolarité"),
    "notes": os.path.join(ACT, "Diplômes & relevés", "Relevés de notes"),
    "attestation": os.path.join(ACT, "Attestations & certificats"),
    "banque": os.path.join(ACT, "Finances & impôts", "BANQUES"),
    "enav": os.path.join(ACT, "Alternance & candidatures", "E-NAVSYSTEMS"),
    "alternance": os.path.join(ACT, "Alternance & candidatures"),
    "electronique": os.path.join(GL, "04 — DEV & OUTILS", "Datasheets & docs électronique"),
    "cao3d": os.path.join(GL, "04 — DEV & OUTILS", "Modèles 3D téléchargés"),
    "factures": os.path.join(ACT, "Finances & impôts", "FACTURES"),
    "capture": os.path.join(HOME, "Pictures", "Captures"),
    "media": os.path.join(AMB, "Photos & vidéos"),
    "ebook": "CALIBRE",
    "installeur": "QUARANTAINE",
}

# Première règle qui correspond = destination. Les noms sont comparés sans accents, en minuscules.
REGLES = [
    ("installeur", r"\.(dmg|pkg|ipa|msi|exe|apk)$|installer|^vscode-darwin|^pokemon-|brain-training"),
    ("ebook", r"\.(epub|azw3|mobi)$|48 lois du pouvoir|votre idee va devenir|programmer avec python en s|essentiels du creatif|guide de demarrage rapide - john schember"),
    ("litiges", r"plainte|recepisse|reclamation|litige|mise en demeure"),
    ("nps_site", r"naitpoolservices\.fr|dmarc"),
    ("nps_carte", r"carte-visite|cartes_de_visite"),
    ("nps_flyer", r"flyer-nps|flyer nps"),
    ("nps_logo", r"logo-nps"),
    ("nps", r"\bnps\b|naitpool|nait pool|ovhcloud|publicite _ facebook"),
    ("paie", r"bulletin.{0,4}de.{0,3}(paie|salaire)|mypeopledoc"),
    ("impots", r"impot|cfspart|dgfip|avis d.imposition|liasse fiscale"),
    ("immobilier", r"lmnp|immobilier"),
    ("finances", r"dettes|budget"),
    ("sante_examen", r"radio|dicom|\birm\b|echograph|bilan sanguin|analyses? (de )?sang"),
    ("sante_arret", r"arret de travail|arret prolongation|arret prologation|_at_\d|volet 3"),
    ("sante", r"assurance.?maladie|ameli|cpam|courrierdevotrecaisse|ordonnance|mutuelle"),
    ("logement", r"quittance|loyer|\bbail\b|echeance|habitation|garant|dossierfacile|cambriolage|garage"),
    ("vehicule", r"pneu|carte grise|controle technique|immatricul|assurance auto"),
    ("identite", r"passeport|id national|carte.?d.?identit|\bcni\b|\bprocu|^signature "),
    ("scolarite", r"certificat.de.scolarit"),
    ("notes", r"detail.{0,3}des.notes|notes_et_resultats|releve.{0,3}de.notes|diplome|livret complet|toeic|niveau de langue"),
    ("attestation", r"attestation|responsabilit|cvec|crous|payfip"),
    ("banque", r"\brib\b|\biban\b|sepa|recouvrement|cloture|banque"),
    ("enav", r"e-navsystems|\benav\b"),
    ("alternance", r"^cv\b|^cv ?\d|lettre de motivation|candidature|acceptation offre|france.travail|7speaking|rapport_activite|rapport d.activite|\besrf\b|convention de stage|cerfa|etemptation|demandes absences|calendrier alternance"),
    ("electronique", r"datasheet|max31856|tps61023|mcp73833|ntc 10k|18650|thermocouple|jlcpcb|kicad|fr-s01"),
    ("cao3d", r"\.snapshot\.|shapr3d|\.(step|stp|stl|igs|iges|sldprt|sldasm|f3d|usdz|3mf)$|elevateur-de-manege"),
    ("factures", r"factur|invoice|receipt|\brecu\b|\border\b|commande|vinted|amazon|panier|devis"),
    ("capture", r"capture d.?ecran|screenshot|^pasted graphic"),
    ("media", r"^(img_|dji_|pxl_|dsc|mvimg|\d{8}_\d{6}).*\.(heic|jpe?g|png|gif|webp|dng|mov|mp4|m4v|mpg|avi)$|\.(heic|mov|mp4|m4v|mpg|avi)$"),
]
# Règles personnelles (noms de fichiers précis, plaque, démarches…) : gardées hors du dépôt Git,
# dans ~/.rangeur/regles-perso.json, liste de [clé, expression]. Elles passent avant les règles générales.
_PERSO = os.path.join(HOME, ".rangeur", "regles-perso.json")
if os.path.exists(_PERSO):
    try:
        with open(_PERSO, encoding="utf-8") as _f:
            REGLES = [tuple(r) for r in json.load(_f)] + REGLES
    except (OSError, ValueError):
        pass
REGLES = [(k, re.compile(rx)) for k, rx in REGLES]
PARTIELS = (".crdownload", ".download", ".part", ".partial", ".tmp")
ICLOUD = [os.path.join(HOME, "Documents"), os.path.join(HOME, "Desktop"), os.path.join(HOME, "Library", "Mobile Documents")]
ONEDRIVE = [os.path.join(HOME, "Library", "CloudStorage")]


def norm(s):
    s = s.replace("\u2019", "'").replace("\u00a0", " ")
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def classer(nom):
    n = norm(nom)
    for cle, rx in REGLES:
        if rx.search(n):
            return cle
    return None


def espace(p):
    rp = os.path.realpath(p)
    for pre in ICLOUD:
        if rp == pre or rp.startswith(pre + os.sep):
            return "icloud"
    for pre in ONEDRIVE:
        if rp.startswith(pre + os.sep):
            return "onedrive"
    return "local"


def dataless(p):
    try:
        return bool(os.lstat(p).st_flags & SF_DATALESS)
    except (OSError, AttributeError):
        return False


def lire_tout(p):
    with open(p, "rb") as f:
        while f.read(8 << 20):
            pass


def materialiser(p):
    if os.path.isdir(p) and not os.path.islink(p):
        for r, ds, fs in os.walk(p):
            for f in fs:
                q = os.path.join(r, f)
                if not os.path.islink(q):
                    lire_tout(q)
    elif not os.path.islink(p):
        lire_tout(p)


def sha_fichier(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloc in iter(lambda: f.read(8 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def empreinte(p):
    if os.path.islink(p):
        return "lien:" + os.readlink(p)
    if os.path.isdir(p):
        h = hashlib.sha256()
        for r, ds, fs in os.walk(p):
            ds.sort()
            for f in sorted(fs):
                if f == ".DS_Store":
                    continue
                q = os.path.join(r, f)
                h.update(os.path.relpath(q, p).encode("utf-8", "surrogateescape"))
                h.update(empreinte(q).encode())
        return h.hexdigest()
    return sha_fichier(p)


def taille(p):
    if os.path.isdir(p) and not os.path.islink(p):
        t = 0
        for r, ds, fs in os.walk(p):
            for f in fs:
                if f != ".DS_Store":
                    try:
                        t += os.lstat(os.path.join(r, f)).st_size
                    except OSError:
                        pass
        return t
    return os.lstat(p).st_size


def identiques(a, b):
    try:
        if os.path.isdir(a) != os.path.isdir(b) or taille(a) != taille(b):
            return False
        return empreinte(a) == empreinte(b)
    except OSError:
        return False


DUP = re.compile(r"^(?P<base>.+?)(?: \d{1,2}| \(\d{1,2}\)|-\d)(?P<ext>\.[A-Za-z0-9]{1,5})?$")


def original_probable(dossier, nom):
    m = DUP.match(nom)
    if not m:
        return None
    cand = m.group("base") + (m.group("ext") or "")
    if cand == nom:
        return None
    p = os.path.join(dossier, cand)
    return p if os.path.lexists(p) else None


def zip_deja_decompresse(dossier, nom):
    if not nom.lower().endswith(".zip"):
        return None
    d = os.path.join(dossier, nom[:-4])
    if not os.path.isdir(d):
        return None
    try:
        with zipfile.ZipFile(os.path.join(dossier, nom)) as z:
            infos = [i for i in z.infolist() if not i.is_dir() and "__MACOSX" not in i.filename
                     and not i.filename.endswith(".DS_Store")]
            n_zip, t_zip = len(infos), sum(i.file_size for i in infos)
    except Exception:
        return None
    n_dir = t_dir = 0
    for r, ds, fs in os.walk(d):
        for f in fs:
            if f != ".DS_Store":
                n_dir += 1
                t_dir += os.lstat(os.path.join(r, f)).st_size
    return d if (n_zip, t_zip) == (n_dir, t_dir) and n_zip > 0 else None


def chemin_libre(p):
    if not os.path.lexists(p):
        return p
    base, ext = (p, "") if os.path.isdir(p) else os.path.splitext(p)
    i = 2
    while os.path.lexists("%s (%d)%s" % (base, i, ext)):
        i += 1
    return "%s (%d)%s" % (base, i, ext)


def deplacer(src, dossier_dest, eviter_doublon=True):
    """Déplace src dans dossier_dest. Ne remplace jamais rien. Renvoie (statut, destination)."""
    dst = os.path.join(dossier_dest, os.path.basename(src))
    if os.path.lexists(dst):
        if eviter_doublon and identiques(src, dst):
            return "deja_la", dst
        dst = chemin_libre(dst)
    os.makedirs(dossier_dest, exist_ok=True)
    if espace(src) != "local" and espace(src) != espace(dossier_dest):
        materialiser(src)
    try:
        os.rename(src, dst)
    except OSError as e:
        if e.errno != errno.EXDEV:
            raise
        if os.path.isdir(src):
            shutil.copytree(src, dst, symlinks=True)
        else:
            shutil.copy2(src, dst)
        if not identiques(src, dst):
            raise RuntimeError("copie non conforme, original conservé : " + src)
        shutil.rmtree(src) if os.path.isdir(src) else os.remove(src)
    if not os.path.lexists(dst) or os.path.lexists(src):
        raise RuntimeError("déplacement incomplet : " + src)
    return "deplace", dst


def doublon_dans(dossier, src):
    """Renvoie le chemin d'un fichier identique (autre nom) déjà présent dans dossier, sinon None."""
    if os.path.isdir(src) or not os.path.isdir(dossier):
        return None
    t = os.lstat(src).st_size
    for nom in os.listdir(dossier):
        q = os.path.join(dossier, nom)
        try:
            if os.path.isfile(q) and not os.path.islink(q) and os.lstat(q).st_size == t and identiques(src, q):
                return q
        except OSError:
            pass
    return None


def calibre_ajouter(p):
    if not os.path.exists(CALIBREDB):
        return False, "calibre absent"
    try:
        r = subprocess.run([CALIBREDB, "add", "--library-path", CALIBRE_LIB, p],
                           capture_output=True, text=True, timeout=600)
    except Exception as e:
        return False, str(e)
    out = (r.stdout or "") + (r.stderr or "")
    bas = out.lower()
    if r.returncode == 0 and "error" not in bas and "erreur" not in bas and "traceback" not in bas:
        return True, out.strip()
    return False, out.strip()


def affiche(p):
    return "~" + p[len(HOME):] if p.startswith(HOME) else p


def journaliser(src, dst, raison, log_extra=None):
    os.makedirs(STATE, exist_ok=True)
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    with open(JOURNAL_TSV, "a", encoding="utf-8", errors="surrogateescape") as f:
        f.write("%s\t%s\t%s\t%s\n" % (stamp, src, dst, raison))
    if log_extra:
        with open(log_extra, "a", encoding="utf-8", errors="surrogateescape") as f:
            f.write("%s\t%s\n" % (src, dst))


def noter_quarantaine(dossier_q, nom, origine, raison):
    os.makedirs(dossier_q, exist_ok=True)
    idx = os.path.join(dossier_q, "INDEX.md")
    neuf = not os.path.exists(idx)
    with open(idx, "a", encoding="utf-8", errors="surrogateescape") as f:
        if neuf:
            f.write("# Quarantaine — %s\n\nRien ici n'a été supprimé. Chaque ligne : élément, d'où il vient, pourquoi il est là.\n\n"
                    % os.path.basename(dossier_q))
        f.write("- `%s` ← `%s` — %s\n" % (nom, affiche(origine), raison))


def ecrire_journal_md(dossier, entrees):
    if not entrees:
        return
    md = os.path.join(dossier, JOURNAL_MD)
    entete = ("# Où sont mes fichiers ?\n\n"
              "Tenu à jour par le rangeur. Un fichier reste 24 h dans Téléchargements, puis il est rangé. "
              "Rien n'est jamais supprimé : doublons et installeurs vont en quarantaine, ce qui est ambigu va dans "
              "`~/Documents/00 — À trier (ambigus)`.\n\n"
              "Annuler une journée : `python3 ~/dotfiles/rangeur/rangeur.py --annuler AAAA-MM-JJ`\n")
    ancien = ""
    if os.path.exists(md):
        with open(md, encoding="utf-8") as f:
            ancien = f.read()
    corps = ("## " + ancien.split("\n## ", 1)[1]) if "\n## " in ancien else ""
    titre = "## " + datetime.date.today().isoformat()
    lignes = "\n".join("- %s · `%s` → `%s`%s" % (h, nom, dest, (" (%s)" % r) if r else "") for h, nom, dest, r in entrees)
    if corps.startswith(titre + "\n"):
        corps = titre + "\n" + lignes + "\n" + corps[len(titre) + 1:]
    else:
        corps = titre + "\n" + lignes + "\n\n" + corps
    tmp = md + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(entete + "\n" + corps.rstrip() + "\n")
    os.replace(tmp, md)


def planifier(source, min_age, reste, quarantaine, ponctuel):
    maintenant = time.time()
    plan = []
    for nom in sorted(os.listdir(source)):
        if nom in (JOURNAL_MD, ".DS_Store", ".localized") or nom.startswith(".") or nom.lower().endswith(PARTIELS):
            continue
        p = os.path.join(source, nom)
        try:
            st = os.lstat(p)
        except FileNotFoundError:
            continue
        if (maintenant - st.st_ctime) / 3600.0 < min_age:
            continue
        if nom in ponctuel:
            cible, raison = ponctuel[nom]
            plan.append((p, quarantaine if cible == "QUARANTAINE" else cible, "ponctuel", raison))
            continue
        orig = original_probable(source, nom)
        if orig and identiques(p, orig):
            plan.append((p, quarantaine, "doublon", "doublon exact de « %s »" % os.path.basename(orig)))
            continue
        if zip_deja_decompresse(source, nom):
            plan.append((p, quarantaine, "doublon", "zip déjà décompressé à côté"))
            continue
        cle = classer(nom)
        if cle is None:
            plan.append((p, reste, "ambigu", "ambigu"))
        elif DEST[cle] == "QUARANTAINE":
            plan.append((p, quarantaine, cle, "installeur, se retélécharge"))
        elif DEST[cle] == "CALIBRE":
            plan.append((p, "CALIBRE", cle, "livre"))
        else:
            plan.append((p, DEST[cle], cle, ""))
    return plan


def executer(plan, quarantaine, reste, log_extra):
    entrees, erreurs = [], 0
    for p, cible, cle, raison in plan:
        nom = os.path.basename(p)
        if not os.path.lexists(p):
            continue
        try:
            if cible == "CALIBRE":
                ok, msg = calibre_ajouter(p)
                if ok:
                    statut, dst = deplacer(p, quarantaine, eviter_doublon=False)
                    raison = "importé dans Calibre, original en quarantaine"
                else:
                    statut, dst = deplacer(p, os.path.join(reste, "Livres à importer dans Calibre"))
                    raison = "livre, Calibre indisponible"
            else:
                jumeau = doublon_dans(cible, p) if cible != quarantaine else None
                if jumeau:
                    statut, dst = deplacer(p, quarantaine, eviter_doublon=False)
                    raison = "identique à « %s », déjà rangé" % affiche(jumeau)
                else:
                    statut, dst = deplacer(p, cible, eviter_doublon=(cible != quarantaine))
                if statut == "deja_la":
                    statut, dst = deplacer(p, quarantaine, eviter_doublon=False)
                    raison = "déjà présent, identique, dans %s" % affiche(cible)
            if dst.startswith(quarantaine + os.sep):
                noter_quarantaine(quarantaine, os.path.basename(dst), p, raison or cle)
            journaliser(p, dst, raison or cle, log_extra)
            entrees.append((time.strftime("%H:%M"), nom, affiche(os.path.dirname(dst)), raison))
        except Exception as e:
            erreurs += 1
            print("! %s : %s" % (nom, e), file=sys.stderr)
    return entrees, erreurs


def annuler(jour):
    if not os.path.exists(JOURNAL_TSV):
        print("Aucun journal.")
        return
    with open(JOURNAL_TSV, encoding="utf-8", errors="surrogateescape") as f:
        lignes = [l.rstrip("\n").split("\t") for l in f if l.startswith(jour)]
    n = 0
    for stamp, src, dst, raison in reversed(lignes):
        if os.path.lexists(dst) and not os.path.lexists(src):
            os.makedirs(os.path.dirname(src), exist_ok=True)
            os.rename(dst, src)
            n += 1
            print("remis en place :", affiche(src))
    print("%d élément(s) remis en place." % n)


def main():
    ap = argparse.ArgumentParser(description="Range ~/Downloads après 24 h, sans rien supprimer.")
    ap.add_argument("--plan", action="store_true", help="montre ce qui serait fait, ne bouge rien")
    ap.add_argument("--annuler", metavar="AAAA-MM-JJ")
    ap.add_argument("--source", default=DL)
    ap.add_argument("--min-age", type=float, default=24.0, help="âge minimal en heures (défaut 24)")
    ap.add_argument("--reste", default=AMB, help="destination de ce qui est ambigu")
    ap.add_argument("--quarantaine", default=None)
    ap.add_argument("--ponctuel", default=None, help="JSON {nom: [dossier ou QUARANTAINE, raison]}")
    ap.add_argument("--dest", action="append", default=[], help="remplace une destination : cle=chemin")
    ap.add_argument("--log", default=None, help="journal supplémentaire source<TAB>destination")
    ap.add_argument("--journal-md", default=None, help="dossier du journal lisible (défaut : Téléchargements si source = Téléchargements)")
    a = ap.parse_args()
    if a.annuler:
        annuler(a.annuler)
        return
    os.makedirs(STATE, exist_ok=True)
    verrou = open(os.path.join(STATE, "verrou"), "w")
    try:
        fcntl.flock(verrou, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("Un rangement est déjà en cours.")
        return
    for kv in a.dest:
        k, v = kv.split("=", 1)
        DEST[k] = v
    source = os.path.abspath(os.path.expanduser(a.source))
    quarantaine = a.quarantaine or os.path.join(QL, "%s — Rangeur" % datetime.date.today().strftime("%Y-%m"))
    ponctuel = {}
    if a.ponctuel:
        with open(a.ponctuel, encoding="utf-8") as f:
            ponctuel = json.load(f)
    try:
        plan = planifier(source, a.min_age, a.reste, quarantaine, ponctuel)
    except PermissionError:
        print("Accès refusé à %s : donne l'accès complet au disque à /Applications/Rangeur.app "
              "(Réglages Système > Confidentialité et sécurité > Accès complet au disque)." % affiche(source))
        return
    if a.plan:
        for p, cible, cle, raison in plan:
            print("%-14s %s  →  %s%s" % (cle, os.path.basename(p), affiche(cible) if cible != "CALIBRE" else "Calibre",
                                          ("  (%s)" % raison) if raison else ""))
        print("--- %d élément(s)" % len(plan))
        return
    entrees, erreurs = executer(plan, quarantaine, a.reste, a.log)
    jmd = a.journal_md if a.journal_md is not None else (DL if source == DL else "")
    if jmd:
        ecrire_journal_md(jmd, entrees)
    print("%d rangé(s), %d erreur(s)" % (len(entrees), erreurs))


if __name__ == "__main__":
    main()
