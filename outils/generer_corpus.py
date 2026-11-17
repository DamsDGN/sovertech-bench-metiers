"""Fabrique les fichiers reels du corpus (docx, doc, xlsx, xls, csv, pdf, pdf degrades) a partir des sources lisibles.

Usage : python3 outils/generer_corpus.py [--metier notaire] [identifiant ...]
"""
import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

sys.path.insert(0, str(Path(__file__).resolve().parent))
import md  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
METIER = "expert-comptable"
CORPUS = RACINE / METIER / "corpus"
DATE_FIXE = datetime.datetime(2026, 1, 15, 9, 0, 0)
POLICE = Path("/usr/share/fonts/truetype/dejavu")
AUTEUR, BANNIERE = "", ""


def configurer(metier: str):
    global METIER, CORPUS, AUTEUR, BANNIERE
    METIER, CORPUS = metier, RACINE / metier / "corpus"
    org = json.loads((CORPUS / "formats.json").read_text(encoding="utf-8"))["_organisation"]
    AUTEUR = org["auteur_metadonnees"]
    BANNIERE = f"{md.BANDEAU} ({org['nom']}, {org['precision']})"


DEGRADATIONS = {"scan": {"dpi": 200, "rotation": 0.0, "gris": True, "jpeg": None},
                "photo": {"dpi": 150, "rotation": -1.2, "gris": False, "jpeg": 60}}


def enregistrer_polices():
    pdfmetrics.registerFont(TTFont("DejaVu", str(POLICE / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(POLICE / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold")


def vers_docx(meta, blocs, chemin):
    from docx import Document
    from docx.shared import Pt
    d = Document()
    p = d.core_properties
    p.author, p.last_modified_by, p.created, p.modified = AUTEUR, AUTEUR, DATE_FIXE, DATE_FIXE
    p.title = meta.get("titre", "")
    d.styles["Normal"].font.name = "Calibri"
    d.styles["Normal"].font.size = Pt(11)

    def ajouter(par, texte):
        for segment, gras in md.segments_gras(texte):
            r = par.add_run(segment)
            r.bold = gras

    banniere = d.add_paragraph()
    r = banniere.add_run(BANNIERE)
    r.italic, r.font.size = True, Pt(8)
    for genre, contenu in blocs:
        if genre == "p" and contenu.startswith(md.BANDEAU):
            continue
        if genre in ("h1", "h2"):
            d.add_heading(md.sans_gras(contenu), level=1 if genre == "h1" else 2)
        elif genre == "p":
            ajouter(d.add_paragraph(), contenu)
        elif genre in ("ul", "ol"):
            for item in contenu:
                ajouter(d.add_paragraph(style="List Bullet" if genre == "ul" else "List Number"), item)
        elif genre == "table":
            t = d.add_table(rows=len(contenu), cols=len(contenu[0]))
            t.style = "Table Grid"
            for i, rangee in enumerate(contenu):
                for j, cellule in enumerate(rangee):
                    par = t.cell(i, j).paragraphs[0]
                    ajouter(par, cellule)
                    if i == 0:
                        for r in par.runs:
                            r.bold = True
            d.add_paragraph()
    d.save(chemin)


def vers_xlsx(meta, blocs, chemin):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    ws = wb.active
    ws.title = (meta.get("titre", "Feuille")[:28]).replace("/", "-")
    wb.properties.creator, wb.properties.created, wb.properties.modified = AUTEUR, DATE_FIXE, DATE_FIXE
    ws.append([BANNIERE])
    ligne = 2
    for genre, contenu in blocs:
        if genre == "p" and contenu.startswith(md.BANDEAU):
            continue
        if genre in ("h1", "h2"):
            ws.append([md.sans_gras(contenu)])
            ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=13 if genre == "h1" else 11)
        elif genre == "p":
            ws.append([md.sans_gras(contenu)])
        elif genre in ("ul", "ol"):
            for item in contenu:
                ws.append(["- " + md.sans_gras(item)])
        elif genre == "table":
            ws.append([])
            for i, rangee in enumerate(contenu):
                ws.append([md.sans_gras(c) for c in rangee])
                if i == 0:
                    for c in ws[ws.max_row]:
                        c.font = Font(bold=True)
            ws.append([])
    for col in range(1, ws.max_column + 1):
        largeur = max((len(str(c.value)) for c in ws[get_column_letter(col)] if c.value), default=8)
        ws.column_dimensions[get_column_letter(col)].width = min(max(largeur + 2, 10), 70)
    wb.save(chemin)


def vers_csv(meta, blocs, chemin):
    lignes = ["Date;Libellé;Montant"]
    for genre, contenu in blocs:
        if genre == "table" and contenu[0][0].lower() == "date":
            for date, libelle, montant in contenu[1:]:
                lignes.append(f"{date}/2026;{md.sans_gras(libelle)};{md.sans_euro(montant).replace('+', '').replace(chr(160), '').replace(chr(8239), '')}")
    chemin.write_text("﻿" + "\r\n".join(lignes) + "\r\n", encoding="utf-8", newline="")


def vers_pdf(meta, blocs, chemin):
    enregistrer_polices()
    st = getSampleStyleSheet()
    normal = ParagraphStyle("n", parent=st["Normal"], fontName="DejaVu", fontSize=10.5, leading=15)
    h1 = ParagraphStyle("h1", parent=normal, fontName="DejaVu-Bold", fontSize=16, leading=20, spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=normal, fontName="DejaVu-Bold", fontSize=12.5, leading=16, spaceBefore=6, spaceAfter=4)
    petit = ParagraphStyle("p", parent=normal, fontSize=7.5, textColor=colors.grey)
    doc = SimpleDocTemplate(str(chemin), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                            title=meta.get("titre", ""), author=AUTEUR, invariant=1)
    flux = [Paragraph(BANNIERE.replace("&", "&amp;"), petit), Spacer(1, 8)]
    for genre, contenu in blocs:
        if genre == "p" and contenu.startswith(md.BANDEAU):
            continue
        if genre == "h1":
            flux.append(Paragraph(md.vers_reportlab(contenu), h1))
        elif genre == "h2":
            flux.append(Paragraph(md.vers_reportlab(contenu), h2))
        elif genre == "p":
            flux += [Paragraph(md.vers_reportlab(contenu), normal), Spacer(1, 5)]
        elif genre in ("ul", "ol"):
            flux.append(ListFlowable([ListItem(Paragraph(md.vers_reportlab(i), normal)) for i in contenu],
                                     bulletType="bullet" if genre == "ul" else "1", bulletFontName="DejaVu", leftIndent=14))
            flux.append(Spacer(1, 5))
        elif genre == "table":
            donnees = [[Paragraph(md.vers_reportlab(c), ParagraphStyle("c", parent=normal, fontSize=9.5, leading=13)) for c in r] for r in contenu]
            t = Table(donnees, repeatRows=1)
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black), ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            flux += [t, Spacer(1, 8)]
    doc.build(flux)


def degrader(pdf_propre: Path, sortie: Path, mode: str):
    p = DEGRADATIONS[mode]
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", str(p["dpi"]), "-png", str(pdf_propre), str(Path(tmp) / "page")], check=True)
        pages = []
        for f in sorted(Path(tmp).glob("page*.png")):
            img = Image.open(f).convert("RGB")
            if p["rotation"]:
                img = img.rotate(p["rotation"], expand=True, resample=Image.BICUBIC, fillcolor=(255, 255, 255))
            if p["jpeg"]:
                aller_retour = Path(tmp) / (f.stem + ".jpg")
                img.save(aller_retour, "JPEG", quality=p["jpeg"])
                img = Image.open(aller_retour).convert("RGB")
            pages.append(img.convert("L") if p["gris"] else img)
        pages[0].save(sortie, "PDF", resolution=float(p["dpi"]), save_all=True, append_images=pages[1:])


def convertir(source: Path, format_cible: str, sortie: Path):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--convert-to", format_cible, "--outdir", tmp, str(source)],
                       check=True, capture_output=True, timeout=180)
        produit = next(Path(tmp).glob("*." + format_cible))
        shutil.move(str(produit), sortie)


def fabriquer(id_, spec, formats_dir: Path):
    meta, blocs = md.lire_source(CORPUS / "sources" / f"{id_}.md")
    fmt, sortie = spec["format"], formats_dir / f"{id_}.{spec['format']}"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if fmt == "docx":
            vers_docx(meta, blocs, sortie)
        elif fmt == "doc":
            vers_docx(meta, blocs, tmp / "t.docx")
            convertir(tmp / "t.docx", "doc", sortie)
        elif fmt == "xlsx":
            vers_xlsx(meta, blocs, sortie)
        elif fmt == "xls":
            vers_xlsx(meta, blocs, tmp / "t.xlsx")
            convertir(tmp / "t.xlsx", "xls", sortie)
        elif fmt == "csv":
            vers_csv(meta, blocs, sortie)
        elif fmt == "pdf":
            if spec.get("degradation"):
                vers_pdf(meta, blocs, tmp / "t.pdf")
                degrader(tmp / "t.pdf", sortie, spec["degradation"])
            else:
                vers_pdf(meta, blocs, sortie)
        else:
            return None
    return sortie


def main(ids=None):
    formats = json.loads((CORPUS / "formats.json").read_text(encoding="utf-8"))
    dossier = CORPUS / "fichiers"
    dossier.mkdir(exist_ok=True)
    for id_, spec in formats.items():
        if id_.startswith("_") or spec["format"] == "txt" or (ids and id_ not in ids):
            continue
        sortie = fabriquer(id_, spec, dossier)
        print(f"{id_:32s} {spec['format']:5s} {spec.get('degradation') or '':6s} {sortie.stat().st_size:>8,} octets")


if __name__ == "__main__":
    args = sys.argv[1:]
    metier = args.pop(args.index("--metier") + 1) if "--metier" in args else "expert-comptable"
    if "--metier" in args:
        args.remove("--metier")
    configurer(metier)
    main(args or None)
