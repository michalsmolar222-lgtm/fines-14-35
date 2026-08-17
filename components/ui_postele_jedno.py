import streamlit as st
import os

def render_postele_jedno(data_postele_sirky, kategoria_látky, data_ulozne=[]):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🛏️ Konfigurátor čalúnenej postele (šírka 90-140 cm)")
    
    if not data_postele_sirky:
        st.warning("Nenašli sa žiadne postele šírky 90-140. Spusť skript `generate_postele_sirky.py`.")
    else:
        col_b90_1, col_b90_2 = st.columns([1, 1])
        with col_b90_1:
            vybrany_model_90 = st.selectbox("Výber modelu postele:", list(data_postele_sirky.keys()))
            polozky_90 = data_postele_sirky.get(vybrany_model_90, [])
            
            if polozky_90:
                vybrana_polozka_90_idx = st.selectbox(
                    "Výber rozmeru a prevedenia:",
                    range(len(polozky_90)),
                    format_func=lambda i: f"{polozky_90[i]['kod']} ({polozky_90[i][kategoria_látky]} €) - {polozky_90[i]['popis']}"
                )
                polozka_90 = polozky_90[vybrana_polozka_90_idx]
                cena_90 = polozka_90[kategoria_látky]
                
                st.markdown(f"**Model:** {polozka_90.get('popis_modelu','')}")
                st.markdown(f"**Popis:** {polozka_90['popis']}")
                if polozka_90.get('sirka_info'):
                    st.markdown(f"**Šírka:** {polozka_90['sirka_info']}")
                    
                atyp_90 = st.checkbox("Predĺžená dĺžka postele (ATYP + 20 %)", key="atyp_90")
                if atyp_90:
                    cena_90 = cena_90 * 1.20
                    atyp_dlzka_90 = st.selectbox("Požadovaná dĺžka:", ["210 cm", "220 cm"], key="atyp_dlzka_90")
                    
                ulozny_options = [{"Kod": "Žiadny", "Popis": "Bez dodatočného úložného priestoru"}] + data_ulozne
                vybrany_ulozny = st.selectbox(
                    "Dodatočný úložný kontajner k roštom (voliteľné):",
                    ulozny_options,
                    format_func=lambda x: f"{x['Kod']} - {x['Popis']}" if x['Kod'] != 'Žiadny' else x['Popis']
                )
                
                nazov_ulozneho = ""
                if vybrany_ulozny['Kod'] != 'Žiadny':
                    if kategoria_látky == 'pohoda':
                        cena_ulozneho = vybrany_ulozny['Buk_Prirodny']
                    elif kategoria_látky == 'zivot':
                        cena_ulozneho = vybrany_ulozny['Buk_Moreny']
                    else:
                        cena_ulozneho = vybrany_ulozny['Dub_Farebny']
                        
                    cena_90 += cena_ulozneho
                    nazov_ulozneho = f" [+ {vybrany_ulozny['Kod']} kontajner]"
                    
                st.metric("Cena s DPH:", f"{cena_90:.2f} €", f"Látka: {kategoria_látky.capitalize()}")
        
        with col_b90_2:
            st.markdown("**Náhľad a parametre**")
            import os
            img_name = str(vybrany_model_90).replace('/', '_').replace(' ', '_').upper()
            img_path = f"{img_name}.png"
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.info("Kvalitné čalúnené 1-lôžka a postele šírok 90, 110, 120 a 140 cm s úložným priestorom z katalógu FINES (str. 12-13).")

        st.write("---")

        st.write("---")
        if st.button("Vložiť do košíka ➔", type="primary", use_container_width=True, key="btn_b90_cart"):
            nazov_postele_90 = f"Posteľ {polozka_90['kod']}"
            if atyp_90:
                dl = st.session_state.get('atyp_dlzka_90', '210 cm')
                nazov_postele_90 += f" [ATYP Predĺžená na {dl}]"
            nazov_postele_90 += nazov_ulozneho
            st.session_state.kosik.append({
                "typ": "Čalúnená posteľ (90-140)",
                "nazov": nazov_postele_90,
                "polozka": polozka_90,
                "latka": kategoria_látky,
                "cena": cena_90
            })
            st.session_state.current_tab = "📋 2. Košík"
            st.rerun()

# --- 3. ROZKLADACIE KRESLÁ A POHOVKY ---
