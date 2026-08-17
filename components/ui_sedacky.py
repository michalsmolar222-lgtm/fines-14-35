import streamlit as st
import os
import streamlit.components.v1 as components
from components.utils_sedacky import get_rozmery, vytvor_skicu, get_max_connections, over_validitu_zostavy

def render_sedacky(model, data, data_boky, data_nozicky, kategoria_látky):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.info("💡 **Nová funkcia:** Môžete si vybrať z dvoch režimov plánovania.")
    rezim_planovania = st.radio(
        "🎛️ Režim skladania sedačky:",
        [
            "📐 Verzia 1: Sprievodca zostavou (Pôvodné sekvenčné spájanie)",
            "🎨 Verzia 2: Interaktívny 2D CAD Canvas (Voľné ukladanie & mriežka)"
        ],
        horizontal=True,
        key="rezim_planovania_sedacky"
    )
    st.write("---")
    
    if rezim_planovania.startswith("🎨 Verzia 2"):
        from components.ui_canvas_sedacky import render_canvas_sedacky
        render_canvas_sedacky(model, data, data_boky, data_nozicky, kategoria_látky)
        return

    import os
    if model and not "PRÍSLUŠENSTVO" in model.upper():
        c_seda, c_bok = st.columns([2, 1])
        
        nazov_clean = model.replace(",", " ").replace("/", " ").strip().upper()
        first_word = nazov_clean.split()[0] if nazov_clean else ""
        
        candidates = [
            f"{first_word}.png",
            f"{nazov_clean}.png",
            f"{model.strip().upper()}.png",
            f"{model.replace(' ', '_').upper()}.png"
        ]
        
        sofa_img_path = None
        for c in candidates:
            if os.path.exists(c):
                sofa_img_path = c
                break
        
        with c_seda:
            if sofa_img_path and os.path.exists(sofa_img_path):
                st.markdown(f"**Model {model}:**")
                st.image(sofa_img_path, use_container_width=True)
            else:
                st.markdown(f"**Model {model}:**")
                st.markdown('<div class="image-placeholder">Náhľad modelu chýba</div>', unsafe_allow_html=True)
                
        nazov_obrazku = first_word
        with c_bok:
            if st.session_state.get('typ_boku'):
                bok_n = str(st.session_state.typ_boku).replace(" ", "_").replace(".", "").replace("č", "c").upper()
                bok_img_path = f"{nazov_obrazku}_{bok_n}.png"
                bok_img_path_fallback = f"{bok_n}.png"
                
                if os.path.exists(bok_img_path):
                    st.markdown(f"**Bok:**")
                    st.image(bok_img_path, use_container_width=True)
                elif os.path.exists(bok_img_path_fallback):
                    st.markdown(f"**Bok:**")
                    st.image(bok_img_path_fallback, use_container_width=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.write("---")
    if model and "MARVEL" in model.upper():
        with st.expander("🪄 Intuitívne plánovanie (navrhnúť zostavu podľa rozmeru)"):
            col_inp1, col_inp2 = st.columns([2, 1])
            with col_inp1:
                zelana_sirka = st.number_input("Zadaj celkovú požadovanú šírku v cm:", min_value=150, max_value=500, value=250, step=10)
            with col_inp2:
                st.write("")
                st.write("")
                navrh_btn = st.button("Navrhnúť zostavu", type="primary")
                
            if navrh_btn:
                elementy_list = data.get("MARVEL", [])
                start_diely = [el for el in elementy_list if el['kod'] in ["B2P-", "B2R-", "B3P-", "B3R-", "3P", "3R"]]
                stred_diely = [el for el in elementy_list if el['kod'] in ["-2SP-", "-2SR-", "-3SP-", "-3SR-", "ROH"]]
                koniec_diely = [el for el in elementy_list if el['kod'] in ["DU-", "DRO-", "DM-", "1", "2P"]]
                
                najm_rozdiel = 9999
                najm_zostava = []
                
                for s in start_diely if start_diely else [elementy_list[0]]:
                    for k in koniec_diely:
                        sim = [s, k]
                        if not all(over_validitu_zostavy(sim[:i], sim[i]['kod'])[0] for i in range(1, len(sim))): continue
                        s_w = get_rozmery(s['kod'], model)[0]
                        k_w = get_rozmery(k['kod'], model)[0]
                        celk = s_w + k_w
                        rozdiel = abs(celk - zelana_sirka)
                        if rozdiel < najm_rozdiel:
                            najm_rozdiel = rozdiel
                            najm_zostava = sim
                    
                    for m in stred_diely:
                        for k in koniec_diely:
                            sim = [s, m, k]
                            if not all(over_validitu_zostavy(sim[:i], sim[i]['kod'])[0] for i in range(1, len(sim))): continue
                            s_w = get_rozmery(s['kod'], model)[0]
                            m_w = get_rozmery(m['kod'], model)[0]
                            k_w = get_rozmery(k['kod'], model)[0]
                            celk = s_w + m_w + k_w
                            rozdiel = abs(celk - zelana_sirka)
                            if rozdiel < najm_rozdiel:
                                najm_rozdiel = rozdiel
                                najm_zostava = sim
                
                if najm_zostava:
                    st.session_state.vybrane_elementy = najm_zostava
                    st.success(f"✨ Program našiel zostavu s celkovou šírkou {sum([get_rozmery(el['kod'], model)[0] for el in najm_zostava])} cm!")
                    st.rerun()
    
    st.write("---")
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.markdown("### 🖱️ Výber elementov:")
        elementy_modelu = data.get(model, [])
        
        if not elementy_modelu:
            st.info(f"⚠️ Pre model '{model}' sa nenašli v Exceli žiadne elementy.")
        else:
            cols = st.columns(3)
            for i, el in enumerate(elementy_modelu):
                with cols[i % 3]:
                    cena = el[kategoria_látky]
                    
                    mini_skica = vytvor_skicu(el['kod'], model=model, scale=0.45, mini=True, position="left")
                    
                    skica_html = f"""
                    <div class="skica-klikacia" style="height: 100px; display: flex; align-items: center; justify-content: center; margin-bottom: 5px; cursor: pointer; border-radius: 12px; transition: background 0.2s; border: 1px solid #e2e8f0; background-color: #f8fafc;" 
                         title="Klikni pre pridanie: {el['popis']}">
                        {mini_skica}
                    </div>
                    """
                    st.markdown(skica_html, unsafe_allow_html=True)
                        
                    if st.button(f"{el['kod']} \n({cena} €)", key=f"{model}_{i}", help=el['popis'], use_container_width=True, disabled=(cena == 0.0)):
                        if st.session_state.vybrane_elementy:
                            je_ok, chybny_kod = over_validitu_zostavy(st.session_state.vybrane_elementy, el['kod'])
                            if not je_ok:
                                if get_max_connections(chybny_kod) == 0:
                                    st.warning(f"Element '{chybny_kod}' je samostatný a nedá sa spájať do radu.")
                                else:
                                    st.warning(f"Element '{chybny_kod}' má už využité všetky svoje spoje a nedá sa k nemu pripojiť ďalší modul.")
                            else:
                                el_copy = el.copy()
                                st.session_state.vybrane_elementy.append(el_copy)
                                st.rerun()
                        else:
                            el_copy = el.copy()
                            st.session_state.vybrane_elementy.append(el_copy)
                            st.rerun()
    
    with col_right:
        st.markdown("### 🛒 Tvoja zostava:")
        
        if st.session_state.vybrane_elementy:
            poskladany_nazov = "".join([el['kod'] for el in st.session_state.vybrane_elementy])
            celkova_cena = sum([el[kategoria_látky] for el in st.session_state.vybrane_elementy])
            
            st.success(f"**Názov:** {model} {poskladany_nazov}")
            

            st.metric("Priebežná cena:", f"{celkova_cena:.2f} €", f"{kategoria_látky.capitalize()}")
            
            # Default empty values if drawing is skipped
            html_nakres = ""
            sirka, hlbka = 0, 0
            layout_data = []

            if True:
                st.markdown("**Smer rohového zlomu:**")
                rb_cols = st.columns(3)
                if 'turn_angle' not in st.session_state:
                    st.session_state.turn_angle = 90
                with rb_cols[0]:
                    if st.button("↪️ Zalomiť doprava", use_container_width=True,
                                 type="primary" if st.session_state.turn_angle == 90 else "secondary",
                                 key="roh_right"):
                        st.session_state.turn_angle = 90
                        st.rerun()
                with rb_cols[1]:
                    if st.button("↩️ Zalomiť doľava", use_container_width=True,
                                 type="primary" if st.session_state.turn_angle == 270 else "secondary",
                                 key="roh_left"):
                        st.session_state.turn_angle = 270
                        st.rerun()
                with rb_cols[2]:
                    if st.button("➡️ Rovno", use_container_width=True,
                                 type="primary" if st.session_state.turn_angle == 0 else "secondary",
                                 key="roh_straight"):
                        st.session_state.turn_angle = 0
                        st.rerun()
                turn_angle = st.session_state.turn_angle
                                     
                min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
                scale = 1.1
                layout_data = []
                
                current_angle = 0
                
                for i, el in enumerate(st.session_state.vybrane_elementy):
                    w, h = get_rozmery(el['kod'], model)
                    
                    manual_uhol = el.get('manual_uhol', -1)
                    if manual_uhol != -1:
                        current_angle = manual_uhol
                        
                    angle = current_angle
                    
                    curr_world_w = w if angle % 180 == 0 else h
                    curr_world_h = h if angle % 180 == 0 else w
                    
                    ex, ey = 0, 0
                    if i > 0:
                        prev_el = layout_data[i-1]
                        px, py = prev_el['ex'], prev_el['ey']
                        pw, ph = prev_el['world_w'], prev_el['world_h']
                        
                        if current_angle == 0:
                            ex = px + pw
                            ey = py
                        elif current_angle == 90:
                            ex = px + pw - curr_world_w
                            ey = py + ph
                        elif current_angle == 180:
                            ex = px - curr_world_w
                            ey = py + ph - curr_world_h
                        elif current_angle == 270:
                            ex = px
                            ey = py - curr_world_h
                    
                    cx = (ex + curr_world_w/2) * scale
                    cy = (ey + curr_world_h/2) * scale
                    cw_scaled = curr_world_w * scale
                    ch_scaled = curr_world_h * scale
                    
                    min_x = min(min_x, cx - cw_scaled/2)
                    max_x = max(max_x, cx + cw_scaled/2)
                    min_y = min(min_y, cy - ch_scaled/2)
                    max_y = max(max_y, cy + ch_scaled/2)
                    
                    layout_data.append({'cx': cx, 'cy': cy, 'angle': angle, 'w': w, 'h': h, 'ex': ex, 'ey': ey, 'world_w': curr_world_w, 'world_h': curr_world_h})
                    
                    if "ROH" in el['kod'].upper() and manual_uhol == -1:
                        current_angle = (current_angle + turn_angle) % 360
        
                total_W = max_x - min_x if max_x > min_x else 0
                total_H = max_y - min_y if max_y > min_y else 0
                
                sirka = round(total_W / scale) if total_W > 0 else 0
                hlbka = round(total_H / scale) if total_H > 0 else 0
                st.metric("Rozmer pôdorysu (Š x H):", f"{sirka} x {hlbka} cm")
                
                html_nakres = f'<div style="position: relative; width: {total_W + 60}px; height: {total_H + 60}px; margin-bottom: 10px; margin-left: auto; margin-right: auto; padding: 30px; background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 8px;">'
                
                total_items = len(st.session_state.vybrane_elementy)
                for i, el in enumerate(st.session_state.vybrane_elementy):
                    if total_items == 1: pos = "left"
                    elif i == 0: pos = "left"
                    elif i == total_items - 1: pos = "right"
                    else: pos = "middle"
                    
                    final_cx = layout_data[i]['cx'] - min_x + 30
                    final_cy = layout_data[i]['cy'] - min_y + 30
                    
                    html_nakres += vytvor_skicu(el['kod'], model=model, scale=scale, mini=False, position=pos, cx=final_cx, cy=final_cy, angle=layout_data[i]['angle'])
                    
                html_nakres += '</div>'
                st.markdown(html_nakres, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("**📋 Poskladané elementy:**")
                
                for i, el in enumerate(st.session_state.vybrane_elementy):
                    current_val = el.get('manual_uhol', -1)
                    display_angle = layout_data[i]['angle'] if (current_val == -1 and i < len(layout_data)) else (current_val if current_val != -1 else 0)
                    
                    uhol_ikona = {
                        0: "➡️",
                        90: "⬇️",
                        180: "⬅️",
                        270: "⬆️"
                    }.get(display_angle, "➡️")
                    
                    c_num, c_title, c_rot, c_del = st.columns([1, 6, 3, 1])
                    with c_num:
                        st.markdown(f"<div style='text-align:center; font-size:18px; font-weight:bold; color:#64748b; padding-top:8px'>{i+1}</div>", unsafe_allow_html=True)
                    with c_title:
                        st.markdown(f"<div style='padding-top:8px'><b style='font-size:15px'>{el['kod']}</b><br><span style='color:#64748b; font-size:12px'>{el.get('popis','')[:40]} &nbsp;&bull;&nbsp; {el[kategoria_látky]:.0f} €</span></div>", unsafe_allow_html=True)
                    with c_rot:
                        if st.button(f"↻ Otočiť ({uhol_ikona} {display_angle}°)", key=f"rot_{i}", use_container_width=True, help="Otvoč element o 90° v smere hodinových ručičiek"):
                            next_angle = (display_angle + 90) % 360
                            st.session_state.vybrane_elementy[i]['manual_uhol'] = next_angle
                            st.rerun()
                    with c_del:
                        if st.button("❌", key=f"del_{i}", help="Odstrániť element"):
                            st.session_state.vybrane_elementy.pop(i)
                            st.rerun()
            
                
            b1, b2 = st.columns(2)
            with b1:
                if st.button("↩️ Krok späť", use_container_width=True):
                    st.session_state.vybrane_elementy.pop()
                    st.rerun()
            with b2:
                if st.button("🗑️ Začať odznova", use_container_width=True):
                    st.session_state.vybrane_elementy = []
                    st.rerun()
        else:
            st.info("Zatiaľ si nevybral žiadny element. Klikaj na ponuku vľavo alebo vyskúšaj Intuitívne plánovanie.")
    
    # --- JAVASCRIPT PRE KLIKANIE NA SKICE ---
    js_code = """
    <script>
    try {
        const parent = window.parent.document;
        function addListeners() {
            const divs = parent.querySelectorAll('.skica-klikacia');
            divs.forEach(div => {
                if (!div.dataset.listenerAdded) {
                    div.dataset.listenerAdded = '1';
                    div.addEventListener('click', function() {
                        const container = this.closest('.element-container, .stElementContainer');
                        if(container && container.nextElementSibling) {
                            const btn = container.nextElementSibling.querySelector('button');
                            if(btn && !btn.disabled) btn.click();
                        }
                    });
                    div.addEventListener('mouseenter', function() { this.style.backgroundColor = '#e6e9ef'; });
                    div.addEventListener('mouseleave', function() { this.style.backgroundColor = 'transparent'; });
                }
            });
        }
        addListeners();
        const obs = new MutationObserver(addListeners);
        obs.observe(parent.body, {childList: true, subtree: true});
    } catch (e) {
        console.error("Nemozno pridat eventy: ", e);
    }
    </script>
    """
    components.html(js_code, height=0, width=0)

    st.write("---")
    
    st.markdown("### ➕ Doplnky k sedačke")
    pocet_podhlavnikov = st.number_input("Počet podhlavníkov K (ks):", min_value=0, value=0, step=1)
    
    cena_podhlavnika = 0.0
    if pocet_podhlavnikov > 0:
        if kategoria_látky == 'pohoda':
            cena_podhlavnika = 144.5 * pocet_podhlavnikov
        elif kategoria_látky == 'zivot':
            cena_podhlavnika = 154.0 * pocet_podhlavnikov
        else:
            cena_podhlavnika = 175.0 * pocet_podhlavnikov
            
        st.info(f"Cena za {pocet_podhlavnikov}x Podhlavník K: {cena_podhlavnika:.2f} €")
        celkova_cena += cena_podhlavnika
        
    if st.button("Vložiť do košíka ➔", type="primary", use_container_width=True, key="btn_couch_cart"):
        if st.session_state.vybrane_elementy:
            nazov_s_bokom = f"{model} {poskladany_nazov}"
            
            doplnky = []
            if st.session_state.get('typ_boku'):
                doplnky.append(f"{st.session_state.typ_boku}")
            if st.session_state.get('typ_nozicky'):
                doplnky.append(f"Nohy: {st.session_state.typ_nozicky}")
            if pocet_podhlavnikov > 0:
                doplnky.append(f"{pocet_podhlavnikov}x Podhlavník K")
            
            if doplnky:
                nazov_s_bokom += f" ({', '.join(doplnky)})"
                
            st.session_state.kosik.append({
                "typ": "Sedačka",
                "nazov": nazov_s_bokom,
                "model": model,
                "elementy": list(st.session_state.vybrane_elementy),
                "latka": kategoria_látky,
                "cena": celkova_cena,
                "layout_data": layout_data,
                "sirka": sirka,
                "hlbka": hlbka,
                "html_nakres": html_nakres
            })
            st.session_state.vybrane_elementy = []
            st.session_state.current_tab = "📋 2. Košík"
            st.rerun()
        else:
            st.warning("Pridajte aspoň jeden element sedačky.")

