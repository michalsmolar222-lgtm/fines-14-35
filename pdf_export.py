import os
import datetime
from fpdf import FPDF, XPos, YPos

# ---------------------------------------------------------------------------
# Pomocné funkcie – fonty a inicializácia
# ---------------------------------------------------------------------------

def get_font_paths():
    font_path = r"C:\Windows\Fonts\arial.ttf"
    font_bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    if not os.path.exists(font_path):
        font_path = r"C:\Windows\Fonts\dejavusans.ttf"
        font_bold_path = r"C:\Windows\Fonts\dejavusans-bold.ttf"
    return font_path, font_bold_path


def init_pdf():
    pdf = FPDF()
    font_path, font_bold_path = get_font_paths()
    if os.path.exists(font_path):
        pdf.add_font("Arial", "", font_path)
        if os.path.exists(font_bold_path):
            pdf.add_font("Arial", "B", font_bold_path)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    return pdf


def _font(font_path):
    return "Arial" if os.path.exists(font_path) else "helvetica"


# ---------------------------------------------------------------------------
# Grafické komponenty hlavičky a päty
# ---------------------------------------------------------------------------

FINES_DARK  = (15, 23, 42)     # #0f172a
FINES_BLUE  = (30, 58, 138)    # #1e3a8a
FINES_LIGHT = (219, 234, 254)  # #dbeafe
FINES_ACCENT = (37, 99, 235)   # #2563eb
ZEBRA_A     = (248, 250, 252)  # #f8fafc
ZEBRA_B     = (255, 255, 255)  # #ffffff
TEXT_DARK   = (15, 23, 42)
TEXT_MID    = (71, 85, 105)
TEXT_LIGHT  = (148, 163, 184)


def draw_header_banner(pdf, font_family):
    """Tmavý gradient banner s logom a nápisom 'CENOVÁ PONUKA'."""
    # Tmavý obdĺžnik
    pdf.set_fill_color(*FINES_DARK)
    pdf.rect(0, 0, 210, 32, style='F')

    # Modrý akcent pruhy
    pdf.set_fill_color(*FINES_BLUE)
    pdf.rect(0, 28, 210, 4, style='F')

    # Logo
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=8, y=5, h=18)
        except Exception:
            pass

    # Nápis CENOVÁ PONUKA (vpravo)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(font_family, 'B', 16)
    pdf.set_xy(0, 8)
    pdf.cell(200, 8, "CENOVÁ PONUKA", align='R')

    pdf.set_font(font_family, '', 8)
    pdf.set_text_color(*FINES_LIGHT)
    pdf.set_xy(0, 18)
    pdf.cell(200, 5, f"FINES, a.s.  |  Dátum: {datetime.datetime.now().strftime('%d.%m.%Y')}", align='R')

    pdf.set_text_color(*TEXT_DARK)
    pdf.set_y(38)


def draw_footer(pdf, font_family):
    """Pätica s číslom strany a výstrahou o platnosti."""
    page_h = pdf.h
    pdf.set_y(page_h - 14)
    pdf.set_draw_color(*FINES_LIGHT)
    pdf.set_line_width(0.3)
    pdf.line(10, page_h - 14, 200, page_h - 14)

    pdf.set_font(font_family, '', 7)
    pdf.set_text_color(*TEXT_MID)
    pdf.set_x(10)
    pdf.cell(130, 5, "FINES, a.s.  |  Táto ponuka nie je záväznou objednávkou  |  Platnosť 30 dní")
    pdf.set_text_color(*TEXT_LIGHT)
    pdf.cell(0, 5, f"Strana {pdf.page_no()}", align='R')
    pdf.set_text_color(*TEXT_DARK)


class PremiumPDF(FPDF):
    """Rozšírená FPDF trieda s automatickou päticou a logom na každej strane."""

    def __init__(self):
        super().__init__()
        self._font_family = None

    def set_font_family(self, family):
        self._font_family = family

    def header(self):
        # Zavolá sa len pri novej strane (nie na prvej – tú riešime manuálne)
        if self.page_no() > 1 and self._font_family:
            self.set_fill_color(*FINES_BLUE)
            self.rect(0, 0, 210, 6, style='F')
            logo_path = "logo.png"
            if os.path.exists(logo_path):
                try:
                    self.image(logo_path, x=8, y=8, h=10)
                except Exception:
                    pass
            self.set_font(self._font_family, 'B', 9)
            self.set_text_color(*TEXT_MID)
            self.set_xy(0, 8)
            self.cell(200, 6, "CENOVÁ PONUKA  |  FINES, a.s.", align='R')
            self.set_text_color(*TEXT_DARK)
            self.set_y(22)

    def footer(self):
        if self._font_family:
            draw_footer(self, self._font_family)


def init_premium_pdf():
    """Inicializuje PremiumPDF s fontmi a prvou stranou."""
    pdf = PremiumPDF()
    font_path, font_bold_path = get_font_paths()
    if os.path.exists(font_path):
        pdf.add_font("Arial", "", font_path)
        if os.path.exists(font_bold_path):
            pdf.add_font("Arial", "B", font_bold_path)
        pdf.set_font_family("Arial")
    else:
        pdf.set_font_family("helvetica")

    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    return pdf, pdf._font_family


# ---------------------------------------------------------------------------
# Sekcie v dokumente
# ---------------------------------------------------------------------------

def draw_customer_info(pdf, objednavka, font_family):
    if not objednavka:
        return

    # Nadpis sekcie
    pdf.set_fill_color(*FINES_LIGHT)
    pdf.set_font(font_family, 'B', 10)
    pdf.set_text_color(*FINES_BLUE)
    pdf.cell(0, 7, "  Údaje odberateľa", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*TEXT_DARK)
    pdf.ln(2)

    pdf.set_font(font_family, '', 9)

    def row(label, val1, label2="", val2=""):
        pdf.set_font(font_family, 'B', 9)
        pdf.cell(38, 5.5, label, border=0)
        pdf.set_font(font_family, '', 9)
        pdf.cell(55, 5.5, str(val1), border=0)
        if label2:
            pdf.set_font(font_family, 'B', 9)
            pdf.cell(40, 5.5, label2, border=0)
            pdf.set_font(font_family, '', 9)
            pdf.cell(0, 5.5, str(val2), border=0)
        pdf.ln(5.5)

    row("Zákazník:", objednavka.get("zakaznik", ""), "Požad. termín:", objednavka.get("termin", ""))
    row("Adresa:", objednavka.get("adresa", ""), "Doprava:", objednavka.get("doprava", ""))
    row("Kontakt:", objednavka.get("kontakt", ""))

    if objednavka.get("poznamka"):
        pdf.set_font(font_family, 'B', 9)
        pdf.cell(38, 5.5, "Poznámka:", border=0)
        pdf.set_font(font_family, '', 9)
        pdf.multi_cell(0, 5.5, str(objednavka.get("poznamka", "")))
    pdf.ln(4)


def draw_section_title(pdf, font_family, title, color=FINES_BLUE):
    """Farebný nadpis sekcie."""
    pdf.set_font(font_family, 'B', 11)
    pdf.set_text_color(*color)
    pdf.set_draw_color(*FINES_LIGHT)
    pdf.set_line_width(0.5)
    pdf.cell(0, 7, title, border='B', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*TEXT_DARK)
    pdf.ln(2)


def draw_total_box(pdf, font_family, povodna_cena, konecna_cena, cena_dopravy, cena_vynosky):
    """Zvýraznený box s celkovou sumou."""
    priemerna_zlava = (1 - konecna_cena / povodna_cena) * 100 if povodna_cena > 0 else 0
    celkova = konecna_cena + cena_dopravy + cena_vynosky

    if pdf.get_y() + 45 > 260:
        pdf.add_page()

    pdf.ln(4)
    draw_section_title(pdf, font_family, "Cenová rekapitulácia")

    pdf.set_font(font_family, '', 9)

    def price_row(label, value, bold=False):
        if bold:
            pdf.set_font(font_family, 'B', 10)
        else:
            pdf.set_font(font_family, '', 9)
        pdf.cell(90, 6, label)
        pdf.cell(0, 6, value, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if povodna_cena > konecna_cena:
        price_row("Pôvodná cena položiek:", f"{povodna_cena:.2f} EUR")
        price_row(f"Priemerná zľava na položky:", f"- {priemerna_zlava:.1f} %")

    if cena_dopravy > 0:
        price_row("Doprava:", f"{cena_dopravy:.2f} EUR")
    if cena_vynosky > 0:
        price_row("Výnoška:", f"{cena_vynosky:.2f} EUR")

    # Modrý zvýraznený box pre finálnu sumu
    pdf.ln(3)
    box_y = pdf.get_y()
    pdf.set_fill_color(*FINES_BLUE)
    pdf.rect(10, box_y, 190, 13, style='F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(font_family, 'B', 12)
    pdf.set_xy(10, box_y)
    pdf.cell(100, 13, "  SPOLU NA ÚHRADU (s DPH):", border=0)
    pdf.cell(0, 13, f"{celkova:.2f} EUR  ", align='R', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*TEXT_DARK)
    pdf.ln(6)


# ---------------------------------------------------------------------------
# Vykresľovanie položiek košíka
# ---------------------------------------------------------------------------

def draw_item_header(pdf, font_family, idx, item):
    """Hlavičkový riadok pre položku košíka."""
    if pdf.get_y() > 240:
        pdf.add_page()

    pdf.set_fill_color(*FINES_LIGHT)
    pdf.set_font(font_family, 'B', 10)
    pdf.set_text_color(*FINES_BLUE)
    item_zlava = item.get("zlava", 0.0)
    cena_po_zlave = item['cena'] * (1 - item_zlava / 100)

    if item_zlava > 0:
        label = f"  {idx}. {item['nazov']}  |  Pôv.: {item['cena']:.2f} EUR  |  Zľava: {item_zlava:.0f}%  |  Cena: {cena_po_zlave:.2f} EUR"
    else:
        label = f"  {idx}. {item['nazov']}  |  Cena: {item['cena']:.2f} EUR"

    pdf.cell(0, 8, label, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*TEXT_DARK)
    pdf.ln(1)


def draw_sedacka_table(pdf, font_family, zoznam_elementov, latka):
    """Zebra tabuľka s elementmi sedačky."""
    pdf.set_font(font_family, 'B', 8)
    pdf.set_fill_color(*FINES_BLUE)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(25, 6, "Kód", fill=True, border=0)
    pdf.cell(120, 6, "Popis elementu", fill=True, border=0)
    pdf.cell(0, 6, "Cena (EUR)", fill=True, border=0, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*TEXT_DARK)

    for i, el in enumerate(zoznam_elementov):
        if pdf.get_y() > 265:
            pdf.add_page()
        fill_color = ZEBRA_A if i % 2 == 0 else ZEBRA_B
        pdf.set_fill_color(*fill_color)
        pdf.set_font(font_family, '', 8)
        pdf.cell(25, 5.5, el['kod'], fill=True, border=0)
        pdf.cell(120, 5.5, el['popis'][:65], fill=True, border=0)
        pdf.cell(0, 5.5, f"{el.get(latka, 0):.2f}", fill=True, border=0, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)


def draw_sketch(pdf, font_family, layout_data, zoznam_elementov, latka, sirka, hlbka):
    """2D nákres sedačky."""
    if not layout_data or sirka <= 0 or hlbka <= 0:
        return

    needed_sketch_h = 55
    if pdf.get_y() + needed_sketch_h > 265:
        pdf.add_page()

    pdf.set_font(font_family, 'B', 9)
    pdf.set_text_color(*FINES_BLUE)
    pdf.cell(0, 5, f"Nákres zostavy ({sirka} x {hlbka} cm):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*TEXT_DARK)
    pdf.ln(2)

    min_x = min([ld['ex'] for ld in layout_data])
    min_y = min([ld['ey'] for ld in layout_data])
    max_w = 170
    max_h = 45
    scale = min(max_w / sirka, max_h / hlbka)
    offset_x = (210 - (sirka * scale)) / 2
    offset_y = pdf.get_y()

    pdf.set_draw_color(*FINES_BLUE)
    pdf.set_line_width(0.4)

    for i_ld, ld in enumerate(layout_data):
        x = offset_x + (ld['ex'] - min_x) * scale
        y = offset_y + (ld['ey'] - min_y) * scale
        w = ld['world_w'] * scale
        h = ld['world_h'] * scale

        pdf.set_fill_color(*FINES_LIGHT)
        pdf.rect(x, y, w, h, style='DF')

        font_sz = max(5, int(8 * min(scale, 1.2)))
        pdf.set_font(font_family, 'B', font_sz)
        pdf.set_text_color(*FINES_BLUE)
        pdf.set_xy(x, y + (h / 2) - 1.5)
        pdf.cell(w, 3, zoznam_elementov[i_ld]['kod'], align='C')
        pdf.set_text_color(*TEXT_DARK)

    sketch_rendered_h = int(hlbka * scale)
    pdf.set_y(offset_y + sketch_rendered_h + 5)


# ---------------------------------------------------------------------------
# Verejné API – hlavné exportné funkcie
# ---------------------------------------------------------------------------

def draw_customer_info_compat(pdf, objednavka):
    """Spätne kompatibilný wrapper."""
    font_path, _ = get_font_paths()
    ff = _font(font_path)
    draw_customer_info(pdf, objednavka, ff)


def draw_price_info(pdf, latka, zlava, povodna_cena, konecna_cena, objednavka):
    """Spätne kompatibilný wrapper."""
    font_path, _ = get_font_paths()
    ff = _font(font_path)
    cena_dopravy = objednavka.get("cena_dopravy", 0) if objednavka else 0
    cena_vynosky = objednavka.get("cena_vynosky", 0) if objednavka else 0
    draw_total_box(pdf, ff, povodna_cena, konecna_cena, cena_dopravy, cena_vynosky)


def export_bed_to_pdf(celo, korpus, latka, zlava, povodna_cena, konecna_cena, img_paths, objednavka=None):
    kosik = [{
        "typ": "Posteľ",
        "nazov": f"Posteľ {celo['kod']} + {korpus['kod']}",
        "celo": celo,
        "korpus": korpus,
        "latka": latka,
        "cena": povodna_cena,
        "zlava": zlava,
        "celo_img_path": img_paths[0] if len(img_paths) > 0 else None,
        "korpus_img_path": img_paths[1] if len(img_paths) > 1 else None
    }]
    return export_cart_to_pdf(kosik, latka, zlava, povodna_cena, konecna_cena, objednavka)


def export_couch_to_pdf(nazov, zoznam_elementov, latka, zlava, povodna_cena, konecna_cena, objednavka=None, layout_data=None, sirka=0, hlbka=0):
    kosik = [{
        "typ": "Sedačka",
        "nazov": nazov,
        "elementy": zoznam_elementov,
        "latka": latka,
        "cena": povodna_cena,
        "zlava": zlava,
        "layout_data": layout_data,
        "sirka": sirka,
        "hlbka": hlbka
    }]
    return export_cart_to_pdf(kosik, latka, zlava, povodna_cena, konecna_cena, objednavka)


def export_cart_to_pdf(kosik, latka, zlava, povodna_cena, konecna_cena, objednavka=None):
    pdf, font_family = init_premium_pdf()

    # ── Titulná hlavička ──────────────────────────────────────────────────
    draw_header_banner(pdf, font_family)

    # ── Zákazník ──────────────────────────────────────────────────────────
    draw_customer_info(pdf, objednavka, font_family)

    # ── Položky košíka ────────────────────────────────────────────────────
    draw_section_title(pdf, font_family, f"Zoznam položiek ({len(kosik)} ks)")

    for idx, item in enumerate(kosik, 1):
        draw_item_header(pdf, font_family, idx, item)

        if item['typ'] == "Posteľ":
            celo = item['celo']
            korpus = item['korpus']
            pdf.set_font(font_family, '', 9)
            pdf.set_fill_color(*ZEBRA_A)
            pdf.cell(30, 5.5, "Čelo:", fill=True)
            pdf.cell(0, 5.5, f"{celo['kod']} – {celo.get('popis', '')}  ({celo.get(latka, 0):.2f} EUR)", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_fill_color(*ZEBRA_B)
            pdf.cell(30, 5.5, "Korpus:", fill=True)
            pdf.cell(0, 5.5, f"{korpus['kod']} – {korpus.get('popis', '')}  ({korpus.get(latka, 0):.2f} EUR)", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

            img_paths = [item.get('celo_img_path'), item.get('korpus_img_path')]
            if any(img_paths):
                if pdf.get_y() > 230:
                    pdf.add_page()
                y = pdf.get_y()
                current_x = 10
                for img in img_paths:
                    if img and os.path.exists(img):
                        pdf.image(img, x=current_x, y=y, h=30)
                        current_x += 80
                pdf.set_y(y + 33)

        elif item['typ'] in ["Čalúnená posteľ (90-140)", "Rozkladacia pohovka", "Jednolôžko / Váľanda"]:
            p = item.get('polozka') or item.get('pohovka') or item.get('jednolozko') or {}
            pdf.set_font(font_family, '', 9)
            pdf.cell(30, 5.5, f"{item['typ']}:")
            pdf.cell(0, 5.5, f"{item['nazov']}  |  Látka: {item.get('latka', '').capitalize()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if p.get('popis'):
                pdf.cell(30, 5.5, "Popis:")
                pdf.cell(0, 5.5, p.get('popis', ''), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

        elif item['typ'] == "Doplnok":
            doplnok = item.get('doplnok', {})
            pdf.set_font(font_family, '', 9)
            pdf.cell(30, 5.5, "Doplnok:")
            pdf.cell(0, 5.5, item['nazov'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if doplnok.get('popis'):
                pdf.cell(30, 5.5, "Popis:")
                pdf.cell(0, 5.5, doplnok.get('popis', ''), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

        elif item['typ'] == "Drevená posteľ":
            pdf.set_font(font_family, '', 9)
            pdf.cell(30, 5.5, "Drevená posteľ:")
            pdf.cell(0, 5.5, f"{item['nazov']}  |  Prevedenie: {item.get('provedenie', '')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

        elif item['typ'] == "Stolička":
            stolicka = item.get('stolicka', {})
            pdf.set_font(font_family, '', 9)
            pdf.cell(30, 5.5, "Stolička / Kreslo:")
            pdf.cell(0, 5.5, item['nazov'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if stolicka.get('popis'):
                pdf.cell(30, 5.5, "Popis:")
                pdf.cell(0, 5.5, stolicka.get('popis', ''), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

        elif item['typ'] == "Rošt":
            rost = item.get('rost', {})
            pdf.set_font(font_family, '', 9)
            pdf.cell(30, 5.5, "Rošt:")
            pdf.cell(0, 5.5, f"{item['nazov']}  |  Šírka: {rost.get('sirka', '')}  |  Nosnosť: {rost.get('nosnost', '')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

            img_path = item.get('img_path')
            if img_path and os.path.exists(img_path):
                if pdf.get_y() > 230:
                    pdf.add_page()
                y = pdf.get_y()
                pdf.image(img_path, x=10, y=y, h=30)
                pdf.set_y(y + 33)

        elif item['typ'] == "Sedačka":
            draw_sedacka_table(pdf, font_family, item['elementy'], item.get('latka', latka))
            draw_sketch(
                pdf, font_family,
                item.get('layout_data'), item['elementy'], item.get('latka', latka),
                item.get('sirka', 0), item.get('hlbka', 0)
            )

        pdf.ln(2)

    # ── Cenová rekapitulácia ──────────────────────────────────────────────
    cena_dopravy = objednavka.get("cena_dopravy", 0) if objednavka else 0
    cena_vynosky = objednavka.get("cena_vynosky", 0) if objednavka else 0
    draw_total_box(pdf, font_family, povodna_cena, konecna_cena, cena_dopravy, cena_vynosky)

    return bytes(pdf.output())
