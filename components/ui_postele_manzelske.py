import streamlit as st
import os

def render_postele_manzelske(data_postele, kategoria_látky, data_ulozne=[]):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🛏️ Konfigurátor čalúnenej manželskej postele (180/160 cm)")
    
    celo_options = data_postele.get("Čelo", [])
    korpus_options = data_postele.get("Korpus", [])
    dorotea_options = data_postele.get("Dorotea", [])
    
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        st.markdown('<div class="config-step"><span class="config-step-number">1</span><span class="config-step-label">Výber čela</span></div>', unsafe_allow_html=True)
        vybrane_celo_idx = 0
        celo = None
        if celo_options:
            vybrane_celo_idx = st.selectbox(
                "Čelo:", 
                range(len(celo_options)), 
                format_func=lambda i: f"{celo_options[i]['kod']} ({celo_options[i][kategoria_látky]} €) - {celo_options[i].get('sirka_info','')}"
            )
            celo = celo_options[vybrane_celo_idx]
        
        st.markdown('<div class="config-step"><span class="config-step-number">2</span><span class="config-step-label">Výber typu kontajneru / základne</span></div>', unsafe_allow_html=True)
        korpus = None
        
        typy_kontajnerov = {
            "VKL": "Vysoký kontajner s lemom (v. 46 cm)",
            "VKP": "Vysoký kontajner prešitý (v. 46 cm)",
            "VKH": "Vysoký kontajner hladký (v. 46 cm)",
            "SKP": "Stredný kontajner prešitý (v. 38 cm)",
            "SKH": "Stredný kontajner hladký (v. 38 cm)",
            "NKP": "Nízky kontajner prešitý (v. 28 cm)",
            "NKH": "Nízky kontajner hladký (v. 28 cm)",
            "NKM": "Nízky kontajner molitanový (v. 28 cm)",
            "DOROTEA": "Posteľ DOROTEA na 4 nožičkách"
        }
        
        vybrany_typ = st.selectbox(
            "Typ kontajneru:",
            list(typy_kontajnerov.keys()),
            format_func=lambda x: f"{x} - {typy_kontajnerov.get(x, '')}"
        )
        
        st.markdown('<div class="config-step"><span class="config-step-number">3</span><span class="config-step-label">Výber integrovaného roštu / výklopu</span></div>', unsafe_allow_html=True)
        if vybrany_typ == "DOROTEA":
            vyfiltrovane_korpusy = dorotea_options
        else:
            vyfiltrovane_korpusy = [k for k in korpus_options if k.get("typ_kontajneru", "") == vybrany_typ]
            
        if vyfiltrovane_korpusy:
            vybrany_korpus_idx = st.selectbox(
                "Prevedenie roštu / kontajneru:",
                range(len(vyfiltrovane_korpusy)),
                format_func=lambda i: f"{vyfiltrovane_korpusy[i]['kod']} - {vyfiltrovane_korpusy[i].get('popis', '')} ({vyfiltrovane_korpusy[i][kategoria_látky]} €)"
            )
            korpus = vyfiltrovane_korpusy[vybrany_korpus_idx]
        
        if celo and korpus:
            cena_celo = celo[kategoria_látky]
            cena_korpus = korpus[kategoria_látky]
            celkova_cena = cena_celo + cena_korpus
            
            st.success(f"**Vyskladaná posteľ:** {celo['kod']} + {korpus['kod']}")
            
            ulozny_options = [{"Kod": "Žiadny", "Popis": "Bez dodatočného úložného priestoru"}] + data_ulozne
            vybrany_ulozny = st.selectbox(
                "4. Dodatočný úložný kontajner k roštom (voliteľné):",
                ulozny_options,
                format_func=lambda x: f"{x['Kod']} - {x['Popis']}" if x['Kod'] != 'Žiadny' else x['Popis']
            )
            
            nazov_ulozneho = ""
            if vybrany_ulozny['Kod'] != 'Žiadny':
                # Mapovanie látky na drevo pre nacenenie (Pohoda=Prirodny, Zivot=Moreny, Neha=Farebny)
                if kategoria_látky == 'pohoda':
                    cena_ulozneho = vybrany_ulozny['Buk_Prirodny']
                elif kategoria_látky == 'zivot':
                    cena_ulozneho = vybrany_ulozny['Buk_Moreny']
                else:
                    cena_ulozneho = vybrany_ulozny['Dub_Farebny']
                    
                celkova_cena += cena_ulozneho
                nazov_ulozneho = f" [+ {vybrany_ulozny['Kod']} kontajner]"
            
            vybrana_sirka_mp = st.radio("Šírka postele:", ["180 cm", "160 cm"], horizontal=True, key="vybrana_sirka_mp")
            
            atyp_mp = st.checkbox("Predĺžená dĺžka postele (ATYP + 20 %)", key="atyp_mp")
            if atyp_mp:
                celkova_cena = celkova_cena * 1.20
                atyp_dlzka_mp = st.selectbox("Požadovaná dĺžka:", ["210 cm", "220 cm"], key="atyp_dlzka_mp")
                
            st.metric("Celková cena postele:", f"{celkova_cena:.2f} €", f"Látka: {kategoria_látky.capitalize()}")

    with col_p2:
        st.markdown("**Grafika postele (Katalóg Fines)**")
        
        celo_img_path = None
        if celo:
            kod_cela = celo['kod'].strip().upper()
            # Odstránime slovo ČELO pre správne priradenie k obrázku (napr. "AMALA ČELO" -> "AMALA")
            nazov_obrazku = kod_cela.replace("ČELO", "").replace("CELO", "").strip()
            if "(" in nazov_obrazku:
                nazov_obrazku = nazov_obrazku.split("(")[0].strip()
            
            path = f"{nazov_obrazku}.png"
            if os.path.exists(path):
                celo_img_path = path

        korpus_img_path = None
        if korpus:
            kod_korpusu = korpus['kod'].upper()
            prefix = kod_korpusu[:3]
            path = f"{prefix}.png"
            if os.path.exists(path):
                korpus_img_path = path
            elif kod_korpusu.startswith("VK") and os.path.exists("vysoky_korpus.png"):
                korpus_img_path = "vysoky_korpus.png"
            elif kod_korpusu.startswith("SK") and os.path.exists("stredny_korpus.png"):
                korpus_img_path = "stredny_korpus.png"
            elif kod_korpusu.startswith("NK") and os.path.exists("nizky_korpus.png"):
                korpus_img_path = "nizky_korpus.png"

        col_img1, col_img2 = st.columns(2)
        with col_img1:
            if celo_img_path:
                st.markdown("**Čelo:**")
                st.image(celo_img_path, use_container_width=True)
            else:
                st.markdown('<div class="image-placeholder">Náhľad čela</div>', unsafe_allow_html=True)
                
        with col_img2:
            if korpus_img_path:
                st.markdown("**Korpus:**")
                st.image(korpus_img_path, use_container_width=True)
            else:
                st.markdown('<div class="image-placeholder">Náhľad korpusu</div>', unsafe_allow_html=True)

    st.write("---")
    if not (celo and korpus):
        atyp_mp = False

    st.write("---")
    if st.button("Vložiť do košíka ➔", type="primary", use_container_width=True, key="btn_bed_cart"):
        if celo and korpus:
            sir = st.session_state.get('vybrana_sirka_mp', '180 cm')
            nazov_postele = f"Posteľ {celo['kod']} + {korpus['kod']} (Šírka: {sir})"
            if atyp_mp:
                dl = st.session_state.get('atyp_dlzka_mp', '210 cm')
                nazov_postele += f" [ATYP Predĺžená na {dl}]"
            nazov_postele += nazov_ulozneho
            st.session_state.kosik.append({
                "typ": "Posteľ",
                "nazov": nazov_postele,
                "celo": celo,
                "korpus": korpus,
                "latka": kategoria_látky,
                "cena": celkova_cena,
                "celo_img_path": celo_img_path,
                "korpus_img_path": korpus_img_path
            })
            st.session_state.current_tab = "📋 2. Košík"
            st.rerun()
        else:
            st.warning("Vyberte prosím čelo aj korpus.")

# --- 2. ČALÚNENÁ POSTEĽ (šírka 90-140 cm) ---
