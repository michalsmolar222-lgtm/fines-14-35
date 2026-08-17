import streamlit as st
import os

def render_pohovky(data_pohovky, kategoria_látky):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🛋️ Konfigurátor rozkladacích kresiel a pohoviek")
    
    if not data_pohovky:
        st.warning("Nenašli sa žiadne pohovky. Spusť skript `generate_pohovky.py`.")
    else:
        kat_pohovka = st.selectbox("Typ nábytku:", list(data_pohovky.keys()))
        pohovky_list = data_pohovky.get(kat_pohovka, [])
        
        if pohovky_list:
            col_ph1, col_ph2 = st.columns([1, 1])
            with col_ph1:
                vybrana_ph_idx = st.selectbox(
                    "Výber modelu / variantu:",
                    range(len(pohovky_list)),
                    format_func=lambda i: f"{pohovky_list[i]['kod']} ({pohovky_list[i][kategoria_látky]} €)"
                )
                pohovka_item = pohovky_list[vybrana_ph_idx]
                cena_ph = pohovka_item[kategoria_látky]
                
                st.markdown(f"**Model:** {pohovka_item['model']}")
                st.markdown(f"**Popis:** {pohovka_item['popis']}")
                st.metric("Cena s DPH:", f"{cena_ph:.2f} €", f"Látka: {kategoria_látky.capitalize()}")
                
            with col_ph2:
                import os
                model_str = str(pohovka_item['model']).replace('/', '_').replace(' ', '_').upper()
                kod_str = str(pohovka_item['kod']).replace('/', '_').replace(' ', '_').upper()
                base_str = model_str.split('_')[0].split(' ')[0]
                
                img_path = None
                for candidate in [f"{model_str}.png", f"{kod_str}.png", f"{base_str}.png", f"{pohovka_item['model'].upper()}.png"]:
                    if os.path.exists(candidate):
                        img_path = candidate
                        break
                        
                if img_path and os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                else:
                    st.info("Rozkladacie kreslá a pohovky určené aj na každodenné spanie z katalógu FINES (str. 22-24).")

            st.write("---")
            if st.button("Vložiť do košíka ➔", type="primary", use_container_width=True, key="btn_pohovka_cart"):
                st.session_state.kosik.append({
                    "typ": "Rozkladacia pohovka",
                    "nazov": f"{pohovka_item['kod']}",
                    "pohovka": pohovka_item,
                    "latka": kategoria_látky,
                    "cena": cena_ph
                })
                st.session_state.current_tab = "📋 2. Košík"
                st.rerun()

# --- 4. JEDNOLÔŽKA A VÁĽANDY ---
