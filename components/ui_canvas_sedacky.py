import streamlit as st
import json
import streamlit.components.v1 as components
from components.utils_sedacky import get_rozmery, vytvor_skicu

def render_canvas_sedacky(model, data, data_boky, data_nozicky, kategoria_látky):
    st.markdown("#### 🎨 Verzia 2: Interaktívny 2D CAD Canvas (podľa skladanieCanvas)")
    st.caption("Voľné ukladanie elementov na milimetrovú mriežku, rotácia, zrkadlenie a automatické kótovanie rozmerov.")

    elementy_modelu = data.get(model, [])
    if not elementy_modelu:
        st.info(f"⚠️ Pre model '{model}' sa nenašli v cenníku žiadne elementy.")
        return

    # Inicializácia stavu canvasu
    if "canvas_placed_items" not in st.session_state:
        st.session_state.canvas_placed_items = []

    col_cat, col_canvas = st.columns([4, 8])

    with col_cat:
        st.markdown("##### 📦 Katalóg elementov")
        st.caption("Kliknutím na tlačidlo '➕ Pridať' umiestnite diel na plochu.")
        
        # Filtre alebo rýchle šablóny
        with st.expander("⚡ Rýchle predlohy zostáv", expanded=False):
            c_t1, c_t2, c_t3 = st.columns(3)
            with c_t1:
                if st.button("📐 Roh L (vľavo)", use_container_width=True):
                    _aplikuj_sablonu(model, "L_LEFT", elementy_modelu, kategoria_látky)
                    st.rerun()
            with c_t2:
                if st.button("📐 Roh L (vpravo)", use_container_width=True):
                    _aplikuj_sablonu(model, "L_RIGHT", elementy_modelu, kategoria_látky)
                    st.rerun()
            with c_t3:
                if st.button("🛋️ Zostava U", use_container_width=True):
                    _aplikuj_sablonu(model, "U_SHAPE", elementy_modelu, kategoria_látky)
                    st.rerun()

        # Zoznam dostupných modulov
        kat_cols = st.columns(2)
        for i, el in enumerate(elementy_modelu):
            with kat_cols[i % 2]:
                cena = el[kategoria_látky]
                w, h = get_rozmery(el['kod'], model)
                
                mini_skica = vytvor_skicu(el['kod'], model=model, scale=0.38, mini=True, position="left")
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px; margin-bottom: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                    <div style="height: 60px; display: flex; align-items: center; justify-content: center;">
                        {mini_skica}
                    </div>
                    <div style="font-weight: 700; font-size: 0.85rem; color: #1e293b; margin-top: 4px;">{el['kod']}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">{w} × {h} cm &bull; <b style="color: #1e3a8a;">{cena:.0f} €</b></div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"➕ Pridať {el['kod']}", key=f"c2_add_{i}", use_container_width=True, disabled=(cena == 0.0)):
                    _pridaj_na_canvas(el, model, kategoria_látky)
                    st.rerun()

    with col_canvas:
        st.markdown("##### 📐 Pracovný 2D Canvas (Mierka 1:1 v mm)")
        
        placed = st.session_state.canvas_placed_items
        
        # Metriky a ovládacia lišta
        col_c_top1, col_c_top2, col_c_top3, col_c_top4 = st.columns([3, 3, 3, 3])
        
        spolu_cena = sum(item['cena'] for item in placed)
        min_x, min_y, max_x, max_y = _spocitaj_bounds(placed)
        sirka_mm = max(0, max_x - min_x) if placed else 0
        hlbka_mm = max(0, max_y - min_y) if placed else 0
        
        with col_c_top1:
            st.metric("Spolu cena", f"{spolu_cena:.2f} €", f"{kategoria_látky.capitalize()}")
        with col_c_top2:
            st.metric("Rozmer zostavy", f"{sirka_mm/10:.0f} × {hlbka_mm/10:.0f} cm" if placed else "0 × 0 cm")
        with col_c_top3:
            st.metric("Počet modulov", f"{len(placed)} ks")
        with col_c_top4:
            if st.button("🗑️ Vyčistiť canvas", use_container_width=True, disabled=(len(placed) == 0)):
                st.session_state.canvas_placed_items = []
                st.rerun()

        # Interaktívny SVG Canvas
        canvas_svg_html = _vygeneruj_interaktivny_canvas(placed, model)
        st.markdown(canvas_svg_html, unsafe_allow_html=True)

        # Tabuľka / Zoznam umiestnených modulov s akciami
        if placed:
            st.markdown("---")
            st.markdown("##### 🛠️ Umiestnené moduly na canvase:")
            
            for idx, item in enumerate(placed):
                c_idx, c_info, c_rot, c_mir, c_pos, c_del = st.columns([1, 4, 2, 2, 3, 1])
                with c_idx:
                    st.markdown(f"<div style='text-align:center; font-weight:800; color:#1e3a8a; font-size:1.1rem; padding-top:6px;'>#{idx+1}</div>", unsafe_allow_html=True)
                with c_info:
                    st.markdown(f"**{item['kod']}** ({item['w_cm']}×{item['h_cm']} cm) &bull; <span style='color:#1e3a8a; font-weight:bold;'>{item['cena']:.0f} €</span>", unsafe_allow_html=True)
                    st.caption(f"Pozícia: X={item['x']} mm, Y={item['y']} mm | Rotácia: {item['rotation']}°")
                with c_rot:
                    if st.button(f"↻ {item['rotation']}°", key=f"c2_rot_{item['id']}", use_container_width=True, help="Otočiť o 90°"):
                        item['rotation'] = (item['rotation'] + 90) % 360
                        st.rerun()
                with c_mir:
                    mir_lbl = "↔️ Zrkadlo" if not item.get('mirrored') else "↩️ Normál"
                    if st.button(mir_lbl, key=f"c2_mir_{item['id']}", use_container_width=True):
                        item['mirrored'] = not item.get('mirrored', False)
                        st.rerun()
                with c_pos:
                    # Posun modulu
                    cp1, cp2, cp3, cp4 = st.columns(4)
                    with cp1:
                        if st.button("⬅️", key=f"c2_ml_{item['id']}", help="Posun doľava o 100mm"):
                            item['x'] = max(0, item['x'] - 100)
                            st.rerun()
                    with cp2:
                        if st.button("➡️", key=f"c2_mr_{item['id']}", help="Posun doprava o 100mm"):
                            item['x'] += 100
                            st.rerun()
                    with cp3:
                        if st.button("⬆️", key=f"c2_mu_{item['id']}", help="Posun hore o 100mm"):
                            item['y'] = max(0, item['y'] - 100)
                            st.rerun()
                    with cp4:
                        if st.button("⬇️", key=f"c2_md_{item['id']}", help="Posun dole o 100mm"):
                            item['y'] += 100
                            st.rerun()
                with c_del:
                    if st.button("❌", key=f"c2_del_{item['id']}", help="Zmazať diel"):
                        st.session_state.canvas_placed_items.pop(idx)
                        st.rerun()

        # Doplnky a tlačidlo pridať do košíka
        st.markdown("---")
        st.markdown("##### ➕ Doplnky a vloženie do košíka")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            pocet_podhlavnikov = st.number_input("Počet podhlavníkov K (ks):", min_value=0, value=0, step=1, key="c2_podhlavniky")
            cena_podhlavnika = 0.0
            if pocet_podhlavnikov > 0:
                if kategoria_látky == 'pohoda': cena_podhlavnika = 144.5 * pocet_podhlavnikov
                elif kategoria_látky == 'zivot': cena_podhlavnika = 154.0 * pocet_podhlavnikov
                else: cena_podhlavnika = 175.0 * pocet_podhlavnikov
                st.info(f"Cena za {pocet_podhlavnikov}x Podhlavník K: {cena_podhlavnika:.2f} €")
                spolu_cena += cena_podhlavnika

        with col_d2:
            st.write("")
            st.write("")
            if st.button("🛒 Vložiť zostavu z Canvasu do košíka ➔", type="primary", use_container_width=True, disabled=(len(placed) == 0), key="c2_add_to_cart"):
                _vloz_canvas_do_kosika(model, placed, kategoria_látky, spolu_cena, pocet_podhlavnikov, sirka_mm, hlbka_mm)
                st.rerun()

def _pridaj_na_canvas(el, model, kategoria_látky):
    import uuid
    w, h = get_rozmery(el['kod'], model)
    w_mm = w * 10
    h_mm = h * 10
    
    placed = st.session_state.canvas_placed_items
    if not placed:
        next_x = 400
        next_y = 400
    else:
        last = placed[-1]
        last_w = last['w_cm'] * 10 if last['rotation'] % 180 == 0 else last['h_cm'] * 10
        next_x = last['x'] + last_w
        next_y = last['y']
        if next_x + w_mm > 4800:
            next_x = 400
            next_y = last['y'] + (last['h_cm'] * 10) + 100

    item = {
        "id": str(uuid.uuid4())[:8],
        "kod": el['kod'],
        "popis": el.get('popis', ''),
        "cena": float(el[kategoria_látky]),
        "w_cm": w,
        "h_cm": h,
        "x": next_x,
        "y": next_y,
        "rotation": 0,
        "mirrored": False
    }
    placed.append(item)

def _spocitaj_bounds(placed):
    if not placed:
        return 0, 0, 0, 0
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')
    for item in placed:
        rot = item.get('rotation', 0)
        w_mm = item['w_cm'] * 10 if rot % 180 == 0 else item['h_cm'] * 10
        h_mm = item['h_cm'] * 10 if rot % 180 == 0 else item['w_cm'] * 10
        
        min_x = min(min_x, item['x'])
        min_y = min(min_y, item['y'])
        max_x = max(max_x, item['x'] + w_mm)
        max_y = max(max_y, item['y'] + h_mm)
    return min_x, min_y, max_x, max_y

def _vygeneruj_interaktivny_canvas(placed, model):
    canvas_w = 5200
    canvas_h = 3000
    
    min_x, min_y, max_x, max_y = _spocitaj_bounds(placed)
    has_items = len(placed) > 0
    
    svg_elements = []
    
    # 1. Mriežka (Grid) 100mm krok
    for x in range(0, canvas_w + 1, 200):
        opacity = "0.25" if x % 1000 == 0 else "0.1"
        svg_elements.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{canvas_h}" stroke="#94a3b8" stroke-width="1.5" stroke-opacity="{opacity}" />')
    for y in range(0, canvas_h + 1, 200):
        opacity = "0.25" if y % 1000 == 0 else "0.1"
        svg_elements.append(f'<line x1="0" y1="{y}" x2="{canvas_w}" y2="{y}" stroke="#94a3b8" stroke-width="1.5" stroke-opacity="{opacity}" />')

    # 2. Umiestnené moduly
    for idx, item in enumerate(placed):
        x = item['x']
        y = item['y']
        w = item['w_cm'] * 10
        h = item['h_cm'] * 10
        rot = item.get('rotation', 0)
        mirrored = item.get('mirrored', False)
        kod = item['kod']
        
        # Stred otáčania
        cx = x + w / 2
        cy = y + h / 2
        
        transform_parts = []
        if rot != 0:
            transform_parts.append(f"rotate({rot} {cx} {cy})")
        if mirrored:
            transform_parts.append(f"translate({cx} {cy}) scale(-1, 1) translate(-{cx} -{cy})")
            
        trans_attr = f'transform="{" ".join(transform_parts)}"' if transform_parts else ""
        
        # Detail kresby sedačky (opierka, sedák, lem)
        arm_w = 180
        back_h = 210
        
        # Tvar elementu
        kod_u = kod.upper()
        fill_color = "#ffffff"
        stroke_color = "#1e3a8a"
        
        shape_svg = f'''
        <g {trans_attr}>
            <!-- Telo modulu -->
            <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="15" fill="{fill_color}" stroke="{stroke_color}" stroke-width="6" />
            <!-- Zadná opierka -->
            <rect x="{x+6}" y="{y+6}" width="{w-12}" height="{back_h}" rx="8" fill="#e2e8f0" stroke="#64748b" stroke-width="3" />
            <!-- Sedák -->
            <rect x="{x+10}" y="{y+back_h+10}" width="{w-20}" height="{h-back_h-20}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2" />
        '''
        
        # Boky (ak ide o koncový diel)
        if kod_u.startswith("B") or kod_u == "1" or "2P" in kod_u or "3P" in kod_u:
            shape_svg += f'<rect x="{x+6}" y="{y+6}" width="{arm_w}" height="{h-12}" rx="8" fill="#cbd5e1" stroke="#64748b" stroke-width="3" />'
        if kod_u == "1" or "2P" in kod_u or "3P" in kod_u:
            shape_svg += f'<rect x="{x+w-arm_w-6}" y="{y+6}" width="{arm_w}" height="{h-12}" rx="8" fill="#cbd5e1" stroke="#64748b" stroke-width="3" />'

        # Kód a číslovanie
        shape_svg += f'''
            <circle cx="{x+40}" cy="{y+40}" r="26" fill="#1e3a8a" />
            <text x="{x+40}" y="{y+49}" font-family="Inter, sans-serif" font-weight="bold" font-size="24" fill="#ffffff" text-anchor="middle">{idx+1}</text>
            <text x="{cx}" y="{cy+30}" font-family="Inter, sans-serif" font-weight="bold" font-size="44" fill="#0f172a" text-anchor="middle">{kod}</text>
            <text x="{cx}" y="{cy+80}" font-family="Inter, sans-serif" font-size="28" fill="#64748b" text-anchor="middle">{item["w_cm"]} × {item["h_cm"]} cm</text>
        </g>
        '''
        svg_elements.append(shape_svg)

    # 3. Kótovacie čiary (CAD Dimension Lines)
    if has_items:
        dim_top_y = max(80, min_y - 120)
        dim_left_x = max(80, min_x - 120)
        
        # Horná kóta (Šírka)
        svg_elements.append(f'''
        <g stroke="#2563eb" stroke-width="3" fill="#2563eb">
            <line x1="{min_x}" y1="{dim_top_y}" x2="{max_x}" y2="{dim_top_y}" />
            <line x1="{min_x}" y1="{dim_top_y-30}" x2="{min_x}" y2="{dim_top_y+30}" />
            <line x1="{max_x}" y1="{dim_top_y-30}" x2="{max_x}" y2="{dim_top_y+30}" />
            <!-- Šípky -->
            <polygon points="{min_x},{dim_top_y} {min_x+25},{dim_top_y-10} {min_x+25},{dim_top_y+10}" />
            <polygon points="{max_x},{dim_top_y} {max_x-25},{dim_top_y-10} {max_x-25},{dim_top_y+10}" />
            <rect x="{(min_x+max_x)/2 - 130}" y="{dim_top_y - 45}" width="260" height="40" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="2" />
            <text x="{(min_x+max_x)/2}" y="{dim_top_y - 18}" font-family="Inter, sans-serif" font-weight="bold" font-size="26" fill="#1e3a8a" text-anchor="middle">Šírka: {(max_x-min_x)/10:.0f} cm ({max_x-min_x} mm)</text>
        </g>
        ''')
        
        # Ľavá kóta (Hĺbka)
        svg_elements.append(f'''
        <g stroke="#2563eb" stroke-width="3" fill="#2563eb">
            <line x1="{dim_left_x}" y1="{min_y}" x2="{dim_left_x}" y2="{max_y}" />
            <line x1="{dim_left_x-30}" y1="{min_y}" x2="{dim_left_x+30}" y2="{min_y}" />
            <line x1="{dim_left_x-30}" y1="{max_y}" x2="{dim_left_x+30}" y2="{max_y}" />
            <!-- Šípky -->
            <polygon points="{dim_left_x},{min_y} {dim_left_x-10},{min_y+25} {dim_left_x+10},{min_y+25}" />
            <polygon points="{dim_left_x},{max_y} {dim_left_x-10},{max_y-25} {dim_left_x+10},{max_y-25}" />
            <g transform="rotate(-90 {dim_left_x} {(min_y+max_y)/2})">
                <rect x="{dim_left_x - 130}" y="{(min_y+max_y)/2 - 45}" width="260" height="40" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="2" />
                <text x="{dim_left_x}" y="{(min_y+max_y)/2 - 18}" font-family="Inter, sans-serif" font-weight="bold" font-size="26" fill="#1e3a8a" text-anchor="middle">Hĺbka: {(max_y-min_y)/10:.0f} cm ({max_y-min_y} mm)</text>
            </g>
        </g>
        ''')

    svg_content = " ".join(svg_elements).replace("\n", "").replace("\r", "").replace("    ", "")
    
    empty_prompt = ""
    if not has_items:
        empty_prompt = f'<text x="{canvas_w/2}" y="{canvas_h/2 - 40}" font-family="Inter, sans-serif" font-weight="bold" font-size="64" fill="#94a3b8" text-anchor="middle">🛋️ Canvas je prázdny</text><text x="{canvas_w/2}" y="{canvas_h/2 + 40}" font-family="Inter, sans-serif" font-size="36" fill="#cbd5e1" text-anchor="middle">Vyberte elementy z katalógu vľavo alebo zvoľte Rýchlu predlohu</text>'

    html = f'<div style="width: 100%; overflow-x: auto; background: #ffffff; border: 2px solid #cbd5e1; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); padding: 12px; margin-bottom: 16px;"><svg viewBox="0 0 {canvas_w} {canvas_h}" style="width: 100%; height: auto; min-width: 600px; max-height: 520px; background: radial-gradient(#f1f5f9 15%, #ffffff 15%); background-size: 20px 20px; border-radius: 12px; border: 1px solid #e2e8f0;">{svg_content}{empty_prompt}</svg></div>'
    return html

def _aplikuj_sablonu(model, typ_sablony, elementy_modelu, kategoria_látky):
    st.session_state.canvas_placed_items = []
    
    # Hľadáme vhodné diely
    start_el = next((el for el in elementy_modelu if el['kod'].startswith("B2") or el['kod'].startswith("B3") or el['kod'].startswith("B1")), elementy_modelu[0])
    roh_el = next((el for el in elementy_modelu if "ROH" in el['kod']), None)
    stred_el = next((el for el in elementy_modelu if el['kod'].startswith("-2") or el['kod'].startswith("-3")), None)
    koniec_el = next((el for el in elementy_modelu if "DU" in el['kod'] or "DM" in el['kod'] or "1" in el['kod'] or "2P" in el['kod']), elementy_modelu[-1])
    
    if typ_sablony == "L_RIGHT":
        _pridaj_na_canvas(start_el, model, kategoria_látky)
        if roh_el:
            _pridaj_na_canvas(roh_el, model, kategoria_látky)
        _pridaj_na_canvas(koniec_el, model, kategoria_látky)
        if len(st.session_state.canvas_placed_items) >= 3:
            st.session_state.canvas_placed_items[2]['rotation'] = 90
            
    elif typ_sablony == "L_LEFT":
        _pridaj_na_canvas(koniec_el, model, kategoria_látky)
        if roh_el:
            _pridaj_na_canvas(roh_el, model, kategoria_látky)
        _pridaj_na_canvas(start_el, model, kategoria_látky)
        if len(st.session_state.canvas_placed_items) >= 3:
            st.session_state.canvas_placed_items[0]['rotation'] = 270

    elif typ_sablony == "U_SHAPE":
        _pridaj_na_canvas(koniec_el, model, kategoria_látky)
        if roh_el: _pridaj_na_canvas(roh_el, model, kategoria_látky)
        if stred_el: _pridaj_na_canvas(stred_el, model, kategoria_látky)
        if roh_el: _pridaj_na_canvas(roh_el, model, kategoria_látky)
        _pridaj_na_canvas(start_el, model, kategoria_látky)

def _vloz_canvas_do_kosika(model, placed, kategoria_látky, spolu_cena, pocet_podhlavnikov, sirka_mm, hlbka_mm):
    poskladany_nazov = "".join([item['kod'] for item in placed])
    nazov_zostavy = f"{model} (Canvas Zostava: {poskladany_nazov})"
    
    doplnky = []
    if st.session_state.get('typ_boku'):
        doplnky.append(f"{st.session_state.typ_boku}")
    if st.session_state.get('typ_nozicky'):
        doplnky.append(f"Nohy: {st.session_state.typ_nozicky}")
    if pocet_podhlavnikov > 0:
        doplnky.append(f"{pocet_podhlavnikov}x Podhlavník K")
        
    if doplnky:
        nazov_zostavy += f" ({', '.join(doplnky)})"
        
    elementy_format = []
    layout_data = []
    for item in placed:
        rot = item.get('rotation', 0)
        w_cm = item['w_cm']
        h_cm = item['h_cm']
        if rot % 180 != 0:
            w_cm, h_cm = h_cm, w_cm
            
        layout_data.append({
            'ex': item['x'] / 10,
            'ey': item['y'] / 10,
            'world_w': w_cm,
            'world_h': h_cm
        })
        
        elementy_format.append({
            "kod": item['kod'],
            "popis": item['popis'],
            kategoria_látky: item['cena'],
            "pohoda": item['cena'] if kategoria_látky == 'pohoda' else 0.0,
            "zivot": item['cena'] if kategoria_látky == 'zivot' else 0.0,
            "neha": item['cena'] if kategoria_látky == 'neha' else 0.0,
            "manual_uhol": rot
        })
        
    st.session_state.kosik.append({
        "typ": "Sedačka",
        "nazov": nazov_zostavy,
        "model": model,
        "elementy": elementy_format,
        "latka": kategoria_látky,
        "cena": spolu_cena,
        "sirka": round(sirka_mm / 10),
        "hlbka": round(hlbka_mm / 10),
        "layout_data": layout_data,
        "html_nakres": _vygeneruj_interaktivny_canvas(placed, model)
    })
    
    st.session_state.canvas_placed_items = []
    st.session_state.current_tab = "📋 2. Košík"
    st.success("Zostava z Canvasu bola úspešne pridaná do košíka!")
