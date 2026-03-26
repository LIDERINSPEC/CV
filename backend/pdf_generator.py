from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import io
import os

LIDER_BLUE = colors.HexColor('#25437A')
LIDER_GOLD = colors.HexColor('#BF9000')
LIDER_GRAY = colors.HexColor('#7F7F7F')
WHITE      = colors.white
BLACK      = colors.black

LOGO_PATH = os.path.join(os.path.dirname(__file__), "lider_logo.png")


def S(name, **kw):
    return ParagraphStyle(name, **kw)

name_style    = S('Name',    fontName='Helvetica-Bold',    fontSize=20, textColor=LIDER_BLUE,  leading=24)
city_style    = S('City',    fontName='Helvetica',         fontSize=9,  textColor=LIDER_GRAY,  leading=12)
title_style   = S('Title',   fontName='Helvetica',         fontSize=11, textColor=LIDER_GOLD,  leading=14)
section_style = S('Section', fontName='Helvetica-Bold',    fontSize=10, textColor=WHITE,       leading=13)
company_style = S('Company', fontName='Helvetica-Bold',    fontSize=9,  textColor=LIDER_GOLD,  leading=11)
job_style     = S('Job',     fontName='Helvetica-Bold',    fontSize=9.5,textColor=LIDER_BLUE,  leading=12)
date_style    = S('Date',    fontName='Helvetica-Oblique', fontSize=8.5,textColor=LIDER_GRAY,  leading=11)
body_style    = S('Body',    fontName='Helvetica',         fontSize=8.5,textColor=BLACK,       leading=12, alignment=TA_JUSTIFY)
bullet_style  = S('Bullet',  fontName='Helvetica',         fontSize=8.5,textColor=BLACK,       leading=12, leftIndent=10, firstLineIndent=-8, alignment=TA_JUSTIFY)
label_style   = S('Label',   fontName='Helvetica-Bold',    fontSize=8.5,textColor=LIDER_BLUE,  leading=12)
footer_style  = S('Footer',  fontName='Helvetica',         fontSize=7,  textColor=LIDER_GRAY,  alignment=TA_CENTER)


def section_header(title):
    t = Table([[Paragraph(title, section_style)]], colWidths=[18 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), LIDER_BLUE),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
    ]))
    return t


def b(text):
    return Paragraph(f"• {text}", bullet_style)


def two_col_list(items):
    half = (len(items) + 1) // 2
    left  = items[:half]
    right = items[half:]
    rows = []
    for i in range(max(len(left), len(right))):
        l = b(left[i])  if i < len(left)  else Paragraph("", body_style)
        r = b(right[i]) if i < len(right) else Paragraph("", body_style)
        rows.append([l, r])
    t = Table(rows, colWidths=[9 * cm, 9 * cm])
    t.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING',    (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return t


def gerar_pdf_lider(data: dict) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm,  bottomMargin=1.5*cm
    )

    story = []

    # ── HEADER ──────────────────────────────────────────────────────
    if os.path.exists(LOGO_PATH):
        logo = RLImage(LOGO_PATH, width=4.5*cm, height=2.1*cm)
    else:
        logo = Paragraph("<b>LÍDER</b>", label_style)

    ht = Table([[Paragraph(data.get("nome", ""), name_style), logo]],
               colWidths=[12*cm, 6*cm])
    ht.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',  (1, 0),  (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(ht)
    story.append(Paragraph(data.get("cidade", ""), city_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(data.get("titulo", ""), title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=LIDER_GOLD, spaceAfter=6))

    # ── PERFIL ───────────────────────────────────────────────────────
    if data.get("perfil"):
        story.append(section_header("PERFIL PROFISSIONAL"))
        story.append(Spacer(1, 4))
        story.append(Paragraph(data["perfil"], body_style))
        story.append(Spacer(1, 6))

    # ── COMPETÊNCIAS ─────────────────────────────────────────────────
    if data.get("competencias"):
        story.append(section_header("COMPETÊNCIAS TÉCNICAS"))
        story.append(Spacer(1, 4))
        story.append(two_col_list(data["competencias"]))
        story.append(Spacer(1, 6))

    # ── CLIENTES ─────────────────────────────────────────────────────
    if data.get("clientes"):
        story.append(section_header("PRINCIPAIS CLIENTES E USUÁRIOS FINAIS"))
        story.append(Spacer(1, 4))
        story.append(Paragraph(" • ".join(data["clientes"]), body_style))
        story.append(Spacer(1, 6))

    # ── HISTÓRICO PROFISSIONAL ────────────────────────────────────────
    if data.get("experiencias"):
        story.append(section_header("HISTÓRICO PROFISSIONAL"))
        story.append(Spacer(1, 6))
        for exp in data["experiencias"]:
            story.append(Paragraph(exp.get("empresa", ""), company_style))
            story.append(Paragraph(exp.get("cargo", ""), job_style))
            story.append(Paragraph(exp.get("periodo", ""), date_style))
            story.append(Spacer(1, 3))
            for bullet in exp.get("bullets", []):
                story.append(b(bullet))
            story.append(Spacer(1, 8))

    # ── FORMAÇÃO ─────────────────────────────────────────────────────
    if data.get("formacao"):
        story.append(section_header("FORMAÇÃO ACADÊMICA"))
        story.append(Spacer(1, 4))
        rows = []
        for f in data["formacao"]:
            curso = f.get("curso", "")
            inst  = f"{f.get('instituicao', '')} | {f.get('ano', '')}"
            rows.append([Paragraph(curso, label_style), Paragraph(inst, body_style)])
        et = Table(rows, colWidths=[6*cm, 12*cm])
        et.setStyle(TableStyle([
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING',    (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(et)
        story.append(Spacer(1, 6))

    # ── CERTIFICAÇÕES ─────────────────────────────────────────────────
    if data.get("certificacoes"):
        story.append(section_header("CERTIFICAÇÕES PROFISSIONAIS"))
        story.append(Spacer(1, 4))
        story.append(two_col_list(data["certificacoes"]))
        story.append(Spacer(1, 6))

    # ── CURSOS ────────────────────────────────────────────────────────
    if data.get("cursos"):
        story.append(section_header("CURSOS E TREINAMENTOS"))
        story.append(Spacer(1, 4))
        story.append(two_col_list(data["cursos"]))
        story.append(Spacer(1, 6))

    # ── FOOTER ────────────────────────────────────────────────────────
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=LIDER_GOLD))
    story.append(Paragraph(
        "Documento elaborado pela Líder Inspeções Quality Experts | ValueAddingPartners",
        footer_style
    ))

    doc.build(story)
    return buffer.getvalue()
