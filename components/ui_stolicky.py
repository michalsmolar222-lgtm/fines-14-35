import streamlit as st
import os

def render_stolicky(data_stolicky):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🪑 Konfigurátor stoličiek a relaxačných kresiel")
    
    if not data_stolicky:
        st.warning("Nenašli sa žiadne stoličky. Spusť skript `generate_chairs.py` pre vygenerovanie `program_stolicky.xlsx`.")
    else:
        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            vybrana_stolicka_idx = st.selectbox(
                "Výber stoličky / kresla:",
                range(len(data_stolicky)),
                format_func=lambda i: f"{data_stolicky[i]['kod']}"
            )
            stolicka = data_stolicky[vybrana_stolicka_idx]
            
            if stolicka['cena_fix'] > 0:
                cena_stolicka = stolicka['cena_fix']
                st.info(f"Pevná MOC cena pre tento model: {cena_stolicka:.2f} €")
            else:
                kat_lat = st.selectbox("Výber látky stoličky:", ["Pohoda", "Život", "Neha"]).lower()
                cena_stolicka = stolicka[kat_lat]
                
            st.markdown(f"**Popis / Provedenie:** {stolicka['popis']}")
        with col_s2:
            import os, re
            img_name = str(stolicka['kod']).replace('/', '_').replace(' ', '_').upper()
            
            # Extract short code e.g. SA09, SA63, SA64, SA52, SA58, LOTOS
            short_code = ""
            match = re.search(r'(SA\d+|LOTOS)', stolicka['kod'].upper())
            if match:
                short_code = match.group(1)
                
            img_path = None
            for candidate in [f"{img_name}.png", f"{short_code}.png", f"STOLIČKA_{short_code}.png", f"KRESLO_{short_code}.png"]:
                if candidate and os.path.exists(candidate):
                    img_path = candidate
                    break
                    
            if img_path and os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.info("Kvalitné stoličky a kreslá z katalógu FINES.")

        st.write("---")
        if st.button("Vložiť do košíka ➔", type="primary", use_container_width=True, key="btn_chair_cart"):
            st.session_state.kosik.append({
                "typ": "Stolička",
                "nazov": f"{stolicka['kod']}",
                "stolicka": stolicka,
                "cena": cena_stolicka
            })
            st.session_state.current_tab = "📋 2. Košík"
            st.rerun()

