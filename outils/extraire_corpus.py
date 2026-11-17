"""Extrait le texte de chaque fichier du corpus avec Apache Tika (meme image et meme configuration que la stack de Sover.tech).

Le texte extrait est versionne avec le corpus (extractions/) : le benchmark n'a besoin ni de Docker ni d'OCR pour tourner.
Usage : python3 outils/extraire_corpus.py
"""
import datetime
import hashlib
import json
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CORPUS = RACINE / "expert-comptable" / "corpus"
IMAGE = "apache/tika:4.2.0-1-full"
CONFIGURATION = {"server": {}, "pipes": {"numClients": 4}, "parse-context": {"tesseract-ocr-parser": {"language": "fra+eng"}}}
PORT = 19998
CONTENEUR = "bench-metiers-tika"


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
    main()
