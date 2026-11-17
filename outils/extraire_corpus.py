"""Extrait le texte de chaque fichier du corpus avec Apache Tika (meme image et meme configuration que la stack de Sover.tech).

Le texte extrait est versionne avec le corpus (extractions/) : le benchmark n'a besoin ni de Docker ni d'OCR pour tourner.
Moteurs : tika (reference, extractions/) ou docling (variante, extractions-docling/, avec conversion LibreOffice prealable des .doc et .xls).
Usage : python3 outils/extraire_corpus.py [tika|docling [identifiant ...]] [--metier expert-comptable]
Avec des identifiants, docling n'extrait que ces documents et conserve le reste du manifeste.
"""
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
METIER = "expert-comptable"
CORPUS = RACINE / METIER / "corpus"
IMAGE = "apache/tika:4.2.0-1-full"
CONFIGURATION = {"server": {}, "pipes": {"numClients": 4}, "parse-context": {"tesseract-ocr-parser": {"language": "fra+eng"}}}
PORT = 19998
CONTENEUR = "bench-metiers-tika"
IMAGE_DOCLING = "ghcr.io/docling-project/docling-serve-cpu:v1.38.2"
PARAMETRES_DOCLING = {"image_export_mode": "placeholder", "table_mode": "accurate", "to_formats": "md", "force_ocr": "true", "ocr_lang": ["fr", "en"]}
CONVERSIONS = {"doc": "docx", "xls": "xlsx"}
TYPES_MIME = {"docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "doc": "application/msword",
              "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xls": "application/vnd.ms-excel",
              "csv": "text/csv", "pdf": "application/pdf", "txt": "text/plain"}
PORT_DOCLING = 15001
CONTENEUR_DOCLING = "bench-metiers-docling"


def sha256(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()


def attendre(url, delai=180):
    debut = time.time()
    while time.time() - debut < delai:
        try:
            urllib.request.urlopen(url, timeout=3).read()
            return
        except (urllib.error.URLError, OSError):
            time.sleep(2)
    raise SystemExit("Tika ne repond pas")


def extraire(chemin: Path) -> str:
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/tika", data=chemin.read_bytes(), method="PUT",
                                 headers={"Accept": "text/plain", "Content-Disposition": f'attachment; filename="{chemin.name}"'})
    texte = urllib.request.urlopen(req, timeout=300).read().decode("utf-8", errors="replace")
    lignes = [l.rstrip() for l in texte.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lignes and not lignes[0]:
        lignes.pop(0)
    while lignes and not lignes[-1]:
        lignes.pop()
    return "\n".join(lignes) + "\n"


def nettoyer(texte: str) -> str:
    lignes = [l.rstrip() for l in texte.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lignes and not lignes[0]:
        lignes.pop(0)
    while lignes and not lignes[-1]:
        lignes.pop()
    return "\n".join(lignes) + "\n"


def convertir_heritage(fichier: Path, dossier: Path) -> tuple:
    """Docling ne lit pas .doc et .xls : conversion prealable avec LibreOffice (traitee comme une etape du pipeline)."""
    cible = CONVERSIONS[fichier.suffix[1:]]
    subprocess.run(["soffice", "--headless", "--convert-to", cible, "--outdir", str(dossier), str(fichier)], check=True, capture_output=True, timeout=180)
    return dossier / f"{fichier.stem}.{cible}", cible


def extraire_docling(chemin: Path, format_: str) -> str:
    import requests
    r = requests.post(f"http://127.0.0.1:{PORT_DOCLING}/v1/convert/file", files={"files": (chemin.name, chemin.read_bytes(), TYPES_MIME[format_])},
                      data=PARAMETRES_DOCLING, timeout=900)
    r.raise_for_status()
    j = r.json()
    if j.get("status") != "success":
        raise SystemExit(f"Docling a echoue sur {chemin.name} : {j.get('errors')}")
    return nettoyer(j["document"]["md_content"])


def lancer_conteneur(nom, port_hote, port_conteneur, args, url_sante):
    subprocess.run(["docker", "rm", "-f", nom], capture_output=True)
    subprocess.run(["docker", "run", "-d", "--rm", "--name", nom, "-p", f"127.0.0.1:{port_hote}:{port_conteneur}"] + args, check=True, capture_output=True)
    attendre(url_sante)


def main_docling(ids=()):
    formats = json.loads((CORPUS / "formats.json").read_text(encoding="utf-8"))
    sortie = CORPUS / "extractions-docling"
    sortie.mkdir(exist_ok=True)
    lancer_conteneur(CONTENEUR_DOCLING, PORT_DOCLING, 5001, ["-e", "DOCLING_SERVE_ENABLE_UI=false", IMAGE_DOCLING], f"http://127.0.0.1:{PORT_DOCLING}/health")
    existant = CORPUS / "MANIFESTE-docling.json"
    docs = json.loads(existant.read_text(encoding="utf-8"))["documents"] if ids and existant.exists() else {}
    tmp = Path(tempfile.mkdtemp())
    try:
        identifiant = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", IMAGE_DOCLING], capture_output=True, text=True).stdout.strip()
        version_lo = subprocess.run(["soffice", "--version"], capture_output=True, text=True).stdout.strip()
        for id_, spec in formats.items():
            if id_.startswith("_") or (ids and id_ not in ids):
                continue
            fichier, fmt, prealable = CORPUS / "fichiers" / f"{id_}.{spec['format']}", spec["format"], None
            if fmt in CONVERSIONS:
                fichier, fmt = convertir_heritage(fichier, tmp)
                prealable = f"{spec['format']} vers {fmt} avec {version_lo}"
            texte = extraire_docling(fichier, fmt)
            (sortie / f"{id_}.txt").write_text(texte, encoding="utf-8", newline="\n")
            docs[id_] = {"fichier": f"{id_}.{spec['format']}", "format": spec["format"], "degradation": spec.get("degradation"),
                         "conversion_prealable": prealable, "sha256_fichier": sha256((CORPUS / "fichiers" / f"{id_}.{spec['format']}").read_bytes()),
                         "sha256_extraction": sha256(texte.encode("utf-8")), "caracteres_extraction": len(texte)}
            print(f"{id_:32s} {spec['format']:5s} {prealable or '':32s} {len(texte):>7,} caracteres", flush=True)
    finally:
        subprocess.run(["docker", "stop", CONTENEUR_DOCLING], capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
    manifeste = {"extraction": {"outil": IMAGE_DOCLING, "identifiant_image": identifiant, "parametres": PARAMETRES_DOCLING,
                                "date": datetime.date.today().isoformat(),
                                "note": "variante de comparaison : memes reglages que la stack Sover.tech (force_ocr, OCR fra+eng), Markdown ; .doc et .xls convertis au prealable par LibreOffice"},
                 "documents": docs}
    (CORPUS / "MANIFESTE-docling.json").write_text(json.dumps(manifeste, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    formats = json.loads((CORPUS / "formats.json").read_text(encoding="utf-8"))
    config_texte = json.dumps(CONFIGURATION, indent=2)
    subprocess.run(["docker", "rm", "-f", CONTENEUR], capture_output=True)
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Path(tmp) / "tika-config.json"
        cfg.write_text(config_texte, encoding="utf-8")
        subprocess.run(["docker", "run", "-d", "--rm", "--name", CONTENEUR, "-p", f"127.0.0.1:{PORT}:9998",
                        "-v", f"{cfg}:/config/tika-config.json:ro", IMAGE, "-c", "/config/tika-config.json"], check=True, capture_output=True)
        try:
            attendre(f"http://127.0.0.1:{PORT}/tika")
            identifiant = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", IMAGE], capture_output=True, text=True).stdout.strip()
            docs = {}
            for id_, spec in formats.items():
                if id_.startswith("_"):
                    continue
                fichier = CORPUS / "fichiers" / f"{id_}.{spec['format']}"
                texte = extraire(fichier)
                (CORPUS / "extractions").mkdir(exist_ok=True)
                (CORPUS / "extractions" / f"{id_}.txt").write_text(texte, encoding="utf-8", newline="\n")
                docs[id_] = {"fichier": fichier.name, "format": spec["format"], "degradation": spec.get("degradation"),
                             "sha256_fichier": sha256(fichier.read_bytes()), "sha256_extraction": sha256(texte.encode("utf-8")),
                             "octets_fichier": fichier.stat().st_size, "caracteres_extraction": len(texte)}
                print(f"{id_:32s} {spec['format']:5s} {spec.get('degradation') or '':6s} {len(texte):>7,} caracteres")
        finally:
            subprocess.run(["docker", "stop", CONTENEUR], capture_output=True)
    manifeste = {"extraction": {"outil": IMAGE, "identifiant_image": identifiant, "configuration": CONFIGURATION,
                                "configuration_sha256": sha256(config_texte.encode("utf-8")),
                                "date": datetime.date.today().isoformat(),
                                "note": "meme image et meme configuration (OCR fra+eng) que la stack Sover.tech ; texte brut (Accept: text/plain)"},
                 "documents": docs}
    (CORPUS / "MANIFESTE.json").write_text(json.dumps(manifeste, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--metier" in args:
        METIER = args.pop(args.index("--metier") + 1)
        args.remove("--metier")
        CORPUS = RACINE / METIER / "corpus"
    if args[:1] == ["docling"]:
        main_docling(tuple(args[1:]))
    else:
        {"tika": main}[(args[0] if args else "tika")]()
