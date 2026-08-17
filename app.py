import importlib
import pdf_export
import cennik_manager
import components.ui_sedacky
import components.ui_canvas_sedacky

importlib.reload(pdf_export)
importlib.reload(cennik_manager)
importlib.reload(components.ui_sedacky)
importlib.reload(components.ui_canvas_sedacky)

from pdf_export import export_bed_to_pdf, export_couch_to_pdf, export_cart_to_pdf
from cennik_manager import (
    export_do_master_excelu, export_formatovany_cennik,
    import_z_master_excelu, get_statistiku, get_zoznam_zaloh
)

import streamlit as st
import pandas as pd
import os
import base64
import streamlit.components.v1 as components

st.set_page_config(
    page_title="FINES – Konfigurátor cenovej ponuky",
    page_icon="🛋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
if os.path.exists("assets/style.css"):
    with open("assets/style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Premium hlavička s logom ──────────────────────────────────────────────────
def _logo_base64():
    try:
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

_logo_b64 = _logo_base64()
_logo_html = f'<img src="data:image/png;base64,{_logo_b64}" style="height:48px; margin-right:16px;"/>' if _logo_b64 else ""

_logo_img = f'<img src="data:image/png;base64,{_logo_b64}" class="fines-header-logo"/>' if _logo_b64 else ""

st.markdown(f"""
<div class="fines-header">
    {_logo_img}
    <div>
        <div class="fines-header-subtitle">FINES, a.s.</div>
        <div class="fines-header-title">🛋️ Konfigurátor cenovej ponuky</div>
    </div>
    <div class="fines-header-meta">
        <div class="fines-header-version">v3.0</div>
        <div class="fines-header-tagline">Nábytok na mieru</div>
    </div>
</div>
""", unsafe_allow_html=True)

if not os.path.exists("program_all.xlsx"):
    st.error("❌ Súbor 'program_all.xlsx' sa nenašiel v zložke! Uisti sa, že tam je a že si spustil extrakčný skript.")
    st.stop()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_data():
    try:
        df = pd.read_excel("program_all.xlsx")
        vysledok = {}
        d_boky = {}
        d_nozicky = {}
        
        for m in df['Model'].unique():
            vysek = df[df['Model'] == m]
            elementy = []
            for _, row in vysek.iterrows():
                elementy.append({
                    "kod": str(row['Kod']).strip(),
                    "popis": str(row['Popis']).strip(),
                    "pohoda": float(row['Pohoda']) if pd.notna(row['Pohoda']) else 0.0,
                    "zivot": float(row['Zivot']) if pd.notna(row['Zivot']) else 0.0,
                    "neha": float(row['Neha']) if pd.notna(row['Neha']) else 0.0
                })
            vysledok[m] = elementy
            
            # Extract meta from the first row of this model
            first_row = vysek.iloc[0]
            boky_raw = str(first_row.get('Boky_Moznosti', '')).strip()
            nozicky_raw = str(first_row.get('Nozicky_Moznosti', '')).strip()
            
            d_boky[m] = [b.strip() for b in boky_raw.split(',')] if boky_raw and boky_raw != 'nan' else []
            d_nozicky[m] = [n.strip() for n in nozicky_raw.split('|')] if nozicky_raw and nozicky_raw != 'nan' else []
            
        return vysledok, d_boky, d_nozicky
    except Exception as e:
        st.error(f"❌ Nastala chyba pri čítaní Excelu: {e}")
        return {}, {}, {}

data, data_boky, data_nozicky = nacitaj_data()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_postele_v2():
    path = "program_postele_v2.xlsx" if os.path.exists("program_postele_v2.xlsx") else "program_postele.xlsx"
    if not os.path.exists(path):
        return {"Čelo": [], "Korpus": [], "Dorotea": []}
    try:
        df = pd.read_excel(path)
        vysledok = {"Čelo": [], "Korpus": [], "Dorotea": []}
        for _, row in df.iterrows():
            kat = str(row['Kategoria']).strip()
            if kat in vysledok:
                vysledok[kat].append({
                    "kod": str(row['Kod']).strip(),
                    "popis": str(row['Popis']).strip(),
                    "typ_kontajneru": str(row.get('Typ_kontajneru', '')).strip() if pd.notna(row.get('Typ_kontajneru')) else "",
                    "popis_kontajneru": str(row.get('Popis_kontajneru', '')).strip() if pd.notna(row.get('Popis_kontajneru')) else "",
                    "pohoda": float(row['Pohoda']) if pd.notna(row['Pohoda']) else 0.0,
                    "zivot": float(row['Zivot']) if pd.notna(row['Zivot']) else 0.0,
                    "neha": float(row['Neha']) if pd.notna(row['Neha']) else 0.0,
                    "nozicky": str(row.get('Nozicky', '')).strip() if pd.notna(row.get('Nozicky')) else "",
                    "sirka_info": str(row.get('Sirka_info', '')).strip() if pd.notna(row.get('Sirka_info')) else ""
                })
        return vysledok
    except Exception as e:
        return {"Čelo": [], "Korpus": [], "Dorotea": []}

data_postele = nacitaj_postele_v2()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_pohovky():
    if not os.path.exists("program_pohovky.xlsx"):
        return {}
    try:
        df = pd.read_excel("program_pohovky.xlsx")
        vysledok = {}
        for _, row in df.iterrows():
            podkat = str(row['Podkategoria']).strip()
            if podkat not in vysledok:
                vysledok[podkat] = []
            vysledok[podkat].append({
                "model": str(row['Model']).strip(),
                "kod": str(row['Kod']).strip(),
                "popis": str(row['Popis']).strip(),
                "pohoda": float(row['Pohoda']) if pd.notna(row['Pohoda']) else 0.0,
                "zivot": float(row['Zivot']) if pd.notna(row['Zivot']) else 0.0,
                "neha": float(row['Neha']) if pd.notna(row['Neha']) else 0.0
            })
        return vysledok
    except Exception as e:
        return {}

data_pohovky = nacitaj_pohovky()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_jednolozka():
    if not os.path.exists("program_jednolozka.xlsx"):
        return {}
    try:
        df = pd.read_excel("program_jednolozka.xlsx")
        vysledok = {}
        for _, row in df.iterrows():
            podkat = str(row['Podkategoria']).strip()
            if podkat not in vysledok:
                vysledok[podkat] = []
            vysledok[podkat].append({
                "model": str(row['Model']).strip(),
                "kod": str(row['Kod']).strip(),
                "popis": str(row['Popis']).strip(),
                "pohoda": float(row['Pohoda']) if pd.notna(row['Pohoda']) else 0.0,
                "zivot": float(row['Zivot']) if pd.notna(row['Zivot']) else 0.0,
                "neha": float(row['Neha']) if pd.notna(row['Neha']) else 0.0,
                "sirka_info": str(row.get('Sirka_info', '')).strip() if pd.notna(row.get('Sirka_info')) else "",
                "cena_mix": float(row['Cena_mix']) if pd.notna(row.get('Cena_mix')) else 0.0
            })
        return vysledok
    except Exception as e:
        return {}

data_jednolozka = nacitaj_jednolozka()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_postele_sirky():
    if not os.path.exists("program_postele_sirky.xlsx"):
        return {}
    try:
        df = pd.read_excel("program_postele_sirky.xlsx")
        vysledok = {}
        for _, row in df.iterrows():
            m = str(row['Model']).strip()
            if m not in vysledok:
                vysledok[m] = []
            vysledok[m].append({
                "popis_modelu": str(row.get('Popis_modelu', '')).strip(),
                "kod": str(row['Kod']).strip(),
                "popis": str(row['Popis']).strip(),
                "pohoda": float(row['Pohoda']) if pd.notna(row['Pohoda']) else 0.0,
                "zivot": float(row['Zivot']) if pd.notna(row['Zivot']) else 0.0,
                "neha": float(row['Neha']) if pd.notna(row['Neha']) else 0.0,
                "sirka_info": str(row.get('Sirka_info', '')).strip() if pd.notna(row.get('Sirka_info')) else ""
            })
        return vysledok
    except Exception as e:
        return {}

data_postele_sirky = nacitaj_postele_sirky()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_rosty():
    if not os.path.exists("program_rosty.xlsx"):
        return []
    try:
        df = pd.read_excel("program_rosty.xlsx")
        vysledok = []
        for _, row in df.iterrows():
            vysledok.append({
                "kod": str(row['Kod']).strip(),
                "sirka": str(row['Sirka']).strip(),
                "nosnost": str(row['Nosnost']).strip(),
                "cena_moc": float(row['Cena_MOC']) if pd.notna(row['Cena_MOC']) else 0.0,
                "cena_moc_akcia": float(row['Cena_MOC_Akcia']) if pd.notna(row['Cena_MOC_Akcia']) else 0.0
            })
        return vysledok
    except Exception as e:
        return []

data_rosty = nacitaj_rosty()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_masiv():
    if not os.path.exists("program_masiv.xlsx"):
        return []
    try:
        df = pd.read_excel("program_masiv.xlsx")
        vysledok = []
        for _, row in df.iterrows():
            vysledok.append({
                "kod": str(row['Kod']).strip(),
                "popis": str(row['Popis']).strip(),
                "sirka": str(row['Sirka']).strip(),
                "buk_prirodny": float(row['Buk_Prirodny']) if pd.notna(row['Buk_Prirodny']) else 0.0,
                "buk_moreny": float(row['Buk_Moreny']) if pd.notna(row['Buk_Moreny']) else 0.0,
                "dub_farebny": float(row['Dub_Farebny']) if pd.notna(row['Dub_Farebny']) else 0.0
            })
        return vysledok
    except Exception as e:
        return []

data_masiv = nacitaj_masiv()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_ulozne_priestory():
    import json
    if not os.path.exists("program_ulozne_priestory.json"):
        return []
    try:
        with open("program_ulozne_priestory.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

data_ulozne = nacitaj_ulozne_priestory()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_stolicky():
    if not os.path.exists("program_stolicky.xlsx"):
        return []
    try:
        df = pd.read_excel("program_stolicky.xlsx")
        vysledok = []
        for _, row in df.iterrows():
            vysledok.append({
                "kod": str(row['Kod']).strip(),
                "popis": str(row['Popis']).strip(),
                "pohoda": float(row['Pohoda']) if pd.notna(row['Pohoda']) else 0.0,
                "zivot": float(row['Zivot']) if pd.notna(row['Zivot']) else 0.0,
                "neha": float(row['Neha']) if pd.notna(row['Neha']) else 0.0,
                "cena_fix": float(row['Cena_Fix']) if pd.notna(row['Cena_Fix']) else 0.0
            })
        return vysledok
    except Exception as e:
        return []

data_stolicky = nacitaj_stolicky()

@st.cache_data(show_spinner=False, ttl=60)
def nacitaj_doplnky():
    if not os.path.exists("program_doplnky.xlsx"):
        return {}
    try:
        df = pd.read_excel("program_doplnky.xlsx")
        vysledok = {}
        for _, row in df.iterrows():
            kat = str(row['Kategoria']).strip()
            if kat not in vysledok:
                vysledok[kat] = []
            vysledok[kat].append({
                "kod": str(row['Kod']).strip(),
                "popis": str(row['Popis']).strip(),
                "pohoda": float(row['Pohoda']) if pd.notna(row['Pohoda']) else 0.0,
                "zivot": float(row['Zivot']) if pd.notna(row['Zivot']) else 0.0,
                "neha": float(row['Neha']) if pd.notna(row['Neha']) else 0.0,
                "cena_fix": float(row['Cena_Fix']) if pd.notna(row['Cena_Fix']) else 0.0
            })
        return vysledok
    except Exception as e:
        return {}

data_doplnky = nacitaj_doplnky()

def vykresli_objednavkovy_formular(prefix_key):
    st.write("---")
    st.markdown("### 📝 Údaje pre cenovú ponuku / objednávku")
    
    col1, col2 = st.columns(2)
    with col1:
        zakaznik = st.text_input("Zákazník (Meno a priezvisko):", key=f"{prefix_key}_zakaznik")
        adresa = st.text_input("Adresa dodania:", key=f"{prefix_key}_adresa")
        kontakt = st.text_input("Telefón / E-mail:", key=f"{prefix_key}_kontakt")
        poznamka = st.text_area("Poznámka:", key=f"{prefix_key}_poznamka", height=120)
        
    with col2:
        termin = st.date_input("Požadovaný termín dodania:", key=f"{prefix_key}_termin")
        doprava = st.selectbox("Spôsob dopravy:", ["Osobný odber", "Kuriérska služba", "FINES doprava"], key=f"{prefix_key}_doprava")
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            cena_dopravy = st.number_input("Cena dopravy (€):", min_value=0.0, value=0.0, step=5.0, key=f"{prefix_key}_cena_dopravy")
        with col2_2:
            cena_vynosky = st.number_input("Cena za výnosku (€):", min_value=0.0, value=0.0, step=5.0, key=f"{prefix_key}_cena_vynosky")
        
    return {
        "zakaznik": zakaznik,
        "adresa": adresa,
        "kontakt": kontakt,
        "termin": termin.strftime("%d.%m.%Y") if termin else "",
        "doprava": doprava,
        "cena_dopravy": cena_dopravy,
        "cena_vynosky": cena_vynosky,
        "poznamka": poznamka
    }

if not data:
    st.warning("⚠️ Nepodarilo sa načítať dáta z Excelu.")
    st.stop()

if "vybrane_elementy" not in st.session_state:
    st.session_state.vybrane_elementy = []
if "kosik" not in st.session_state:
    st.session_state.kosik = []
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "🛒 1. Produkt"

# ── Visual Stepper ────────────────────────────────────────────────────────────
_pocet_v_kosiku = len(st.session_state.get("kosik", []))
_step_labels = ["Produkt", f"Košík ({_pocet_v_kosiku})", "Dodanie a platba", "Admin"]
_step_icons = ["🛒", "📋", "🚚", "⚙️"]
_step_keys = ["🛒 1. Produkt", "📋 2. Košík", "🚚 3. Dodanie a platba", "⚙️ Admin"]
_current_key = st.session_state.current_tab
_current_idx = 0
for _si, _sk in enumerate(_step_keys):
    if _current_key == _sk:
        _current_idx = _si
        break

_stepper_html = '<div class="stepper-nav">'
for _si in range(len(_step_labels)):
    if _si == _current_idx:
        _cls = "active"
    elif _si < _current_idx:
        _cls = "done"
    else:
        _cls = "inactive"
    _circle_txt = "✓" if _cls == "done" else str(_si + 1)
    _stepper_html += f'<div class="stepper-step {_cls}"><div class="stepper-circle">{_circle_txt}</div><div class="stepper-label">{_step_icons[_si]} {_step_labels[_si]}</div></div>'
    if _si < len(_step_labels) - 1:
        _conn_cls = "done" if _si < _current_idx else ""
        _stepper_html += f'<div class="stepper-connector {_conn_cls}"></div>'
_stepper_html += '</div>'
st.markdown(_stepper_html, unsafe_allow_html=True)

# ── Tab Radio (functional, visually enhanced by CSS) ──
_kosik_label = f"📋 2. Košík ({_pocet_v_kosiku})"
tab_options = ["🛒 1. Produkt", _kosik_label, "🚚 3. Dodanie a platba", "⚙️ Admin"]

_tab_map = {
    "🛒 1. Produkt": "🛒 1. Produkt",
    "📋 2. Košík": _kosik_label,
    "🚚 3. Dodanie a platba": "🚚 3. Dodanie a platba",
    "⚙️ Admin": "⚙️ Admin",
}
_tab_map_inv = {v: k for k, v in _tab_map.items()}

try:
    _display_tab = _tab_map.get(st.session_state.current_tab, tab_options[0])
    default_idx = tab_options.index(_display_tab)
except ValueError:
    default_idx = 0

selected_tab_display = st.radio(
    "Navigácia:",
    tab_options,
    index=default_idx,
    horizontal=True,
    label_visibility="collapsed",
    key=f"tab_radio_{default_idx}"
)

selected_tab = _tab_map_inv.get(selected_tab_display, selected_tab_display)
if selected_tab.startswith("📋 2. Košík"):
    selected_tab = "📋 2. Košík"

if selected_tab != st.session_state.current_tab:
    st.session_state.current_tab = selected_tab
    st.rerun()

current_tab = st.session_state.current_tab
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

if current_tab == "🛒 1. Produkt":
    if "edit_mode_idx" in st.session_state:
        idx = st.session_state.edit_mode_idx
        if idx < len(st.session_state.kosik):
            item = st.session_state.kosik[idx]
            typ_map = {
                "Sedačka": "Sedačka",
                "Posteľ": "Čalúnená manželská posteľ (šírka 180/160)",
                "Čalúnená posteľ (90-140)": "Čalúnená posteľ (šírka 90-140)",
                "Drevená posteľ": "Drevená posteľ a masív",
                "Rozkladacia pohovka": "Rozkladacie kreslá a pohovky",
                "Jednolôžko": "Jednolôžka a váľandy",
                "Rošt": "Rošt",
                "Doplnok": "Doplnky a spálňový nábytok",
                "Jedálenská stolička": "Jedálenské stoličky a relaxačné kreslá",
                "Ušiakové kreslo": "Ušiakové kreslá",
                "Taburetka": "Taburetky"
            }
            st.session_state.typ_nabytku_sel = typ_map.get(item['typ'], "Sedačka")
            
            if item['typ'] == "Sedačka":
                st.session_state.model_sel = item.get('model', 'MARVEL')
                st.session_state.latka_sel = item.get('latka', 'pohoda').capitalize()
                st.session_state.vybrane_elementy = item.get('elementy', [])
                
                nazov_parts = item.get('nazov', '').split('(')
                if len(nazov_parts) > 1:
                    doplnky_str = nazov_parts[-1].strip(')')
                    doplnky = [d.strip() for d in doplnky_str.split(',')]
                    for d in doplnky:
                        if 'Nohy:' in d:
                            st.session_state.noha_sel = d.replace('Nohy: ', '')
                        else:
                            st.session_state.bok_sel = d
            
            st.session_state.edit_item = item
            st.session_state.kosik.pop(idx)
        del st.session_state.edit_mode_idx
        st.rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        typ_nabytku = st.selectbox("Typ nábytku:", [
            "Sedačka",
            "Ušiakové kreslá",
            "Taburetky",
            "Čalúnená manželská posteľ (šírka 180/160)",
            "Čalúnená posteľ (šírka 90-140)",
            "Drevená posteľ a masív",
            "Rozkladacie kreslá a pohovky",
            "Jednolôžka a váľandy",
            "Rošt",
            "Doplnky a spálňový nábytok",
            "Jedálenské stoličky a relaxačné kreslá"
        ], key="typ_nabytku_sel")
    with col2:
        if typ_nabytku in ["Sedačka", "Ušiakové kreslá", "Taburetky"]:
            if typ_nabytku == "Sedačka":
                zoznam_modelov = [m for m in list(data.keys()) if m not in ["KRESLÁ UŠIAKOVÉ", "TABURETKY"]] if data else ["MARVEL"]
                model = st.selectbox("Model:", zoznam_modelov, key="model_sel")
            elif typ_nabytku == "Ušiakové kreslá":
                model = "KRESLÁ UŠIAKOVÉ"
            elif typ_nabytku == "Taburetky":
                model = "TABURETKY"
            
            model_upper = model.upper()
            if "PRÍSLUŠENSTVO" in model_upper:
                st.session_state.typ_boku = None
                st.session_state.typ_nozicky = None
            else:
                dostupne_boky = data_boky.get(model, [])
                if dostupne_boky:
                    st.session_state.typ_boku = st.selectbox("Výber opierky rúk (Bok):", dostupne_boky, key="bok_sel")
                elif "MANIA" in model_upper:
                    st.session_state.typ_boku = st.selectbox("Výber boku:", ["S drevenými bokmi", "Bez bokov"], key="bok_sel")
                else:
                    st.session_state.typ_boku = None
                    
                dostupne_nozicky = data_nozicky.get(model, [])
                if dostupne_nozicky:
                    st.session_state.typ_nozicky = st.selectbox("Výber nožičiek:", dostupne_nozicky, key="noha_sel")
                else:
                    st.session_state.typ_nozicky = None
        else:
            model = None
    with col3:
        if typ_nabytku in ["Sedačka", "Ušiakové kreslá", "Taburetky", "Čalúnená manželská posteľ (šírka 180/160)", "Čalúnená posteľ (šírka 90-140)", "Rozkladacie kreslá a pohovky", "Jednolôžka a váľandy"]:
            kategoria_látky = st.selectbox("Kategória látky:", ["Pohoda", "Zivot", "Neha"], key="latka_sel").lower()
        else:
            kategoria_látky = "pohoda"

    # --- 1. ČALÚNENÁ MANŽELSKÁ POSTEĽ (180/160 cm) ---
    # --- KOMPONENTY ---
    from components.ui_postele_manzelske import render_postele_manzelske
    from components.ui_postele_jedno import render_postele_jedno
    from components.ui_pohovky import render_pohovky
    from components.ui_jednolozka import render_jednolozka
    from components.ui_rosty import render_rosty
    from components.ui_masiv import render_masiv
    from components.ui_stolicky import render_stolicky
    from components.ui_doplnky import render_doplnky
    from components.ui_sedacky import render_sedacky

    if typ_nabytku == "Čalúnená manželská posteľ (šírka 180/160)":
        render_postele_manzelske(data_postele, kategoria_látky, data_ulozne)
    elif typ_nabytku == "Čalúnená posteľ (šírka 90-140)":
        render_postele_jedno(data_postele_sirky, kategoria_látky, data_ulozne)
    elif typ_nabytku == "Rozkladacie kreslá a pohovky":
        render_pohovky(data_pohovky, kategoria_látky)
    elif typ_nabytku == "Jednolôžka a váľandy":
        render_jednolozka(data_jednolozka, kategoria_látky)
    elif typ_nabytku == "Rošt":
        render_rosty(data_rosty)
    elif typ_nabytku == "Drevená posteľ a masív":
        render_masiv(data_masiv, data_ulozne)
    elif typ_nabytku == "Jedálenské stoličky a relaxačné kreslá":
        render_stolicky(data_stolicky)
    elif typ_nabytku == "Doplnky a spálňový nábytok":
        render_doplnky(data_doplnky)
    elif typ_nabytku in ["Sedačka", "Ušiakové kreslá", "Taburetky"]:
        render_sedacky(model, data, data_boky, data_nozicky, kategoria_látky)

if current_tab == "📋 2. Košík":
    st.markdown("## 📋 Váš košík")

    if not st.session_state.kosik:
        st.markdown("""
        <div class="empty-cart">
            <div class="empty-cart-icon">🛒</div>
            <h3>Košík je zatiaľ prázdny</h3>
            <p>
                Vyberte si nábytok v záložke <strong>1. Produkt</strong> a pridajte ho do košíka.
            </p>
        </div>
        """, unsafe_allow_html=True)
        col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
        with col_cta2:
            if st.button("➡️ Prejsť na výber produktu", use_container_width=True, type="primary"):
                st.session_state.current_tab = "🛒 1. Produkt"
                st.rerun()
    else:

        st.write("---")
        import uuid
        for item in st.session_state.kosik:
            if "_id" not in item:
                item["_id"] = str(uuid.uuid4())
            if "zlava" not in item:
                item["zlava"] = 0.0

        for idx, item in enumerate(st.session_state.kosik):
            widget_key = f"zlava_{item['_id']}"
            if widget_key in st.session_state:
                item["zlava"] = st.session_state[widget_key]

            cena_po_zlave = item["cena"] * (1 - item["zlava"] / 100)
            
            # Cart card wrapper
            st.markdown(f'<div class="cart-card">', unsafe_allow_html=True)
            col_item1, col_item2 = st.columns([5, 2])
            with col_item1:
                st.markdown(f'<div class="cart-card-title"><span class="cart-card-number">{idx+1}</span>{item["nazov"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<span class="cart-card-price-original">{item["cena"]:.2f} €</span> <span class="cart-card-price">{cena_po_zlave:.2f} €</span>', unsafe_allow_html=True)
                
                if item['typ'] == "Posteľ":
                    c_i1, c_i2 = st.columns(2)
                    with c_i1:
                        if item.get('celo_img_path'): st.image(item['celo_img_path'], width=150)
                    with c_i2:
                        if item.get('korpus_img_path'): st.image(item['korpus_img_path'], width=150)
                elif item['typ'] == "Rošt":
                    if item.get('img_path') and os.path.exists(item['img_path']):
                        st.image(item['img_path'], width=150)
                elif item['typ'] in ["Čalúnená posteľ (90-140)", "Rozkladacia pohovka", "Jednolôžko / Váľanda"]:
                    p = item.get('polozka') or item.get('pohovka') or item.get('jednolozko') or {}
                    if p.get('popis'):
                        st.caption(f"Popis: {p['popis']}")
                    if item.get('latka'):
                        st.caption(f"Látka: {item['latka'].capitalize()}")
                elif item['typ'] == "Drevená posteľ":
                    st.caption(f"Provedenie: {item.get('provedenie','')}")
                elif item['typ'] == "Doplnok":
                    if item.get('doplnok', {}).get('popis'):
                        st.caption(f"Popis: {item['doplnok']['popis']}")
                elif item['typ'] == "Stolička":
                    if item.get('stolicka', {}).get('popis'):
                        st.caption(f"Popis: {item['stolicka']['popis']}")
                elif item['typ'] == "Sedačka":
                    if item.get('html_nakres'):
                        st.markdown(item['html_nakres'], unsafe_allow_html=True)
            with col_item2:
                st.number_input("Zľava na produkt (%)", min_value=0.0, max_value=100.0, value=float(item["zlava"]), step=1.0, key=widget_key)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✏️ Upraviť", key=f"edit_{item['_id']}"):
                        st.session_state.edit_mode_idx = idx
                        st.session_state.edit_item = item
                        st.session_state.current_tab = "🛒 1. Produkt"
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ Odstrániť", key=f"del_{item['_id']}", type="secondary"):
                        st.session_state.kosik.pop(idx)
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    celkova_cena_bez_zlavy = sum(item['cena'] for item in st.session_state.kosik) if st.session_state.kosik else 0.0
    celkova_cena_po_zlave = sum(item['cena'] * (1 - item.get("zlava", 0.0) / 100) for item in st.session_state.kosik) if st.session_state.kosik else 0.0

    st.markdown("### 🏷️ Celková cena košíka")
    col_z1, col_z2 = st.columns(2)
    with col_z1:
        st.metric("Súčet pôvodných cien:", f"{celkova_cena_bez_zlavy:.2f} €")
    with col_z2:
        st.markdown(f"""
        <div class="total-price-box">
            <h2>Konečná cena: {celkova_cena_po_zlave:.2f} €</h2>
            <p>Cena s DPH po započítaní individuálnych zliav</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    st.markdown("### 💾 Správa cenovej ponuky (Save / Load)")
    import json
    
    col_save, col_load = st.columns(2)
    with col_save:
        st.markdown("**Uložiť rozpracovanú ponuku:**")
        kosik_json = json.dumps(st.session_state.kosik, default=str)
        st.download_button(
            label="⬇️ Stiahnuť ponuku (.json)",
            data=kosik_json,
            file_name="cenova_ponuka_rozpracovana.json",
            mime="application/json",
            use_container_width=True,
            type="primary"
        )
        
    with col_load:
        st.markdown("**Načítať uloženú ponuku:**")
        uploaded_file = st.file_uploader("Nahrajte .json súbor ponuky", type="json")
        if uploaded_file is not None:
            if st.button("Obnoviť košík zo súboru", use_container_width=True):
                try:
                    loaded_kosik = json.load(uploaded_file)
                    st.session_state.kosik = loaded_kosik
                    st.success("Košík bol úspešne obnovený!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Chyba pri načítaní: {e}")

    st.write("---")
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b1:
        if st.button("⬅ Pridať ďalší produkt", use_container_width=True):
            st.session_state.current_tab = "🛒 1. Produkt"
            st.rerun()
    with col_b3:
        if st.button("Pokračovať k dodaniu ➔", type="primary", use_container_width=True, disabled=(len(st.session_state.kosik) == 0)):
            st.session_state.current_tab = "🚚 3. Dodanie a platba"
            st.rerun()

if current_tab == "🚚 3. Dodanie a platba":
    st.markdown("## 🚚 Dodacie údaje")
    objednavka = vykresli_objednavkovy_formular("spolocne")
    
    cena_dopravy = objednavka.get("cena_dopravy", 0.0)
    cena_vynosky = objednavka.get("cena_vynosky", 0.0)
    
    celkova_cena_kosika = sum(item['cena'] for item in st.session_state.kosik) if st.session_state.kosik else 0.0
    konecna_cena = sum(item['cena'] * (1 - item.get("zlava", 0.0) / 100) for item in st.session_state.kosik) if st.session_state.kosik else 0.0
    uplne_konecna = konecna_cena + cena_dopravy + cena_vynosky
    
    st.markdown("### 💰 Finálna kalkulácia")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Cena po zľavách (s DPH)", f"{konecna_cena:.2f} €")
    with col_m2:
        st.metric("Doprava a výnoska", f"{cena_dopravy + cena_vynosky:.2f} €")
    with col_m3:
        priemerna_zlava = (1 - konecna_cena / celkova_cena_kosika) * 100 if celkova_cena_kosika > 0 else 0
        st.metric("Priemerná zľava", f"{priemerna_zlava:.1f} %")
        
    st.markdown(f"""
    <div class="total-price-box">
        <h2>Spolu na úhradu: {uplne_konecna:.2f} €</h2>
        <p>Vrátane dopravy a výnosky</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    col_back, col_space, col_pdf = st.columns([1, 2, 1])
    with col_back:
        if st.button("⬅ Späť do košíka", use_container_width=True):
            st.session_state.current_tab = "📋 2. Košík"
            st.rerun()
            
    with col_pdf:
        if st.button("📄 Generovať PDF ponuku", type="primary", use_container_width=True):
            try:
                latky_v_kosiku = list(set([item.get('latka', 'Nezadané') for item in st.session_state.kosik if 'latka' in item]))
                kategoria_latky_pdf = ", ".join(latky_v_kosiku) if latky_v_kosiku else "Neuvedené"
                
                pdf_data = export_cart_to_pdf(st.session_state.kosik, kategoria_latky_pdf, priemerna_zlava, celkova_cena_kosika, konecna_cena, objednavka)
                st.download_button(
                    label="📄 Stiahnuť PDF ponuku (Celý košík)",
                    data=bytes(pdf_data),
                    file_name="Cenova_ponuka_FINES.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Chyba pri generovaní PDF: {e}")

# ===========================================================================
# ⚙️ ADMIN PANEL – Správa cenníka
# ===========================================================================
elif current_tab == "⚙️ Admin":
    st.markdown("""
    <div class="admin-header">
        <div>
            <h2>⚙️ Správa cenníka</h2>
            <p>Stiahnite, upravte a nahrajte cenníky. Automatická záloha pred každou zmenou.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="admin-section">', unsafe_allow_html=True)

    # --- ŠTATISTIKA ---
    st.markdown("### 📊 Aktuálny stav cenníka")
    stat = get_statistiku()
    nazvy = {
        "Sedacky": "🛋️ Sedačky",
        "Postele_Manzelske": "🛏️ Manž. postele (180/160)",
        "Postele_Sirky": "🛏️ Postele (90–140 cm)",
        "Masiv": "🪵 Masívne postele",
        "Pohovky": "🛋️ Pohovky a rozkladacie kreslá",
        "Jednolozka": "🛏️ Jednolôžka a váľandy",
        "Rosty": "📦 Rošty",
        "Doplnky": "🗃️ Doplnky a spálňový nábytok",
        "Stolicky": "🪑 Jedálenské stoličky a kreslá",
    }
    cols_stat = st.columns(3)
    for i, (klic, pocet) in enumerate(stat.items()):
        with cols_stat[i % 3]:
            farba = "normal" if pocet > 0 else "off"
            st.metric(
                label=nazvy.get(klic, klic),
                value=f"{pocet} pol." if pocet >= 0 else "⚠️ chyba",
            )
    st.write("---")

    # --- EXPORT ---
    col_ex, col_im = st.columns(2)

    with col_ex:
        st.markdown("### 📥 Stiahnuť cenník")
        
        st.markdown("**📋 Formaťtovaný cenník (na zdieľanie / tlač)**")
        st.markdown(
            "Profesionálny Excel s logom FINES, farebnými sekciami "
            "a čitäteľnými názvami. Ideálny ako samostatný cenník pre partnerov."
        )
        platnost_datum = st.date_input("Platnosť cenníka:", key="platnost_datum")
        if st.button("📋 Pripraviť formaťtovaný cenník", use_container_width=True, type="primary", key="btn_export_fmt"):
            try:
                from datetime import date
                platnost_str = platnost_datum.strftime("%d.%m.%Y") if platnost_datum else ""
                excel_bytes = export_formatovany_cennik(platnost_str)
                st.download_button(
                    label="⬇️ Stiahnuť FINES_Cenník.xlsx",
                    data=excel_bytes,
                    file_name=f"FINES_Cenník_{platnost_str.replace('.', '-')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary",
                    key="btn_dl_fmt"
                )
            except Exception as e:
                st.error(f"❌ Chyba pri exporte: {e}")
        
        st.markdown("---")
        st.markdown("**💾 Záloha pre import (technický formát)**")
        st.caption("Súbor pre vás – ak chcete rúčne upraviť dáta a nahrať späť do systému.")
        if st.button("💾 Pripraviť dátovú zálohu", use_container_width=True, key="btn_export_raw"):
            try:
                excel_bytes = export_do_master_excelu()
                st.download_button(
                    label="⬇️ Stiahnuť cennik_master.xlsx",
                    data=excel_bytes,
                    file_name="cennik_master.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="btn_dl_raw"
                )
            except Exception as e:
                st.error(f"❌ Chyba pri exporte: {e}")

    with col_im:
        st.markdown("### 📤 Nahrať aktualizovaný cenník")
        st.markdown(
            """
            Nahrajte upravený `cennik_master.xlsx`. Systém pred zápisom automaticky:
            - ✅ Overí štruktúru (záložky a stĺpce)
            - ✅ Overí, že ceny sú čísla
            - 💾 Uloží zálohu do priečinka `archive/`
            """
        )
        nahrana_file = st.file_uploader(
            "Vyberte cennik_master.xlsx:",
            type=["xlsx"],
            key="uploader_cennik"
        )
        if nahrana_file is not None:
            if st.button("📤 Importovať a uložiť", use_container_width=True, type="primary", key="btn_import_cennik"):
                with st.spinner("Overujem a zapisujem cenník..."):
                    uspech, sprava = import_z_master_excelu(nahrana_file)
                if uspech:
                    st.success(sprava)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(sprava)

    st.write("---")

    # --- ZÁLOHY ---
    st.markdown("### 💾 História zálohy")
    zalohy = get_zoznam_zaloh()
    if zalohy:
        # Zobrazíme unikátne časové značky (nie jednotlivé súbory)
        casove_znacky = sorted(set("_".join(z.split("_")[1:3]) for z in zalohy), reverse=True)
        st.markdown(f"V priečinku `archive/` sa nachádza **{len(casove_znacky)} záloha(y)**:")
        for ts in casove_znacky[:10]:
            datum_str = ts.replace("_", " ").replace("-", ".", 2).replace("-", ":")
            st.markdown(f"- 📁 Záloha zo dňa **{datum_str}**")
        if len(casove_znacky) > 10:
            st.caption(f"... a {len(casove_znacky) - 10} ďalších starších záloh.")
    else:
        st.info("Zatiaľ nebola vykonaná žiadna záloha. Záloha sa automaticky vytvorí pri prvom importe.")

