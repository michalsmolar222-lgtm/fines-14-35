import streamlit as st
import os

def render_doplnky(data_doplnky):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🛋️ Konfigurátor doplnkov ku posteliam a spálňového nábytku")
    
    if not data_doplnky:
        st.warning("Nenašli sa žiadne doplnky. Spusť skript `generate_doplnky.py`.")
    else:
        kat_doplnku = st.selectbox("Kategória doplnku / nábytku:", list(data_doplnky.keys()))
        doplnky_list = data_doplnky.get(kat_doplnku, [])
        
        if doplnky_list:
            col_d1, col_d2 = st.columns([1, 1])
            with col_d1:
                vybrany_doplnok_idx = st.selectbox(
                    "Výber položky:",
                    range(len(doplnky_list)),
                    format_func=lambda i: f"{doplnky_list[i]['kod']} - {doplnky_list[i]['popis']}"
                )
                doplnok = doplnky_list[vybrany_doplnok_idx]
                
                if doplnok['cena_fix'] > 0:
                    cena_doplnok = doplnok['cena_fix']
                    st.info(f"Pevná MOC cena: {cena_doplnok:.2f} €")
                else:
                    kat_lat_d = st.selectbox("Látka / Provedenie:", ["Pohoda", "Život", "Neha"]).lower()
                    cena_doplnok = doplnok[kat_lat_d]
                    
                st.markdown(f"**Popis:** {doplnok['popis']}")
                st.metric("Cena s DPH:", f"{cena_doplnok:.2f} €")
                
            with col_d2:
                st.markdown("**Náhľad a parametre**")
                import os
                img_name = str(doplnok['kod']).replace('/', '_').replace(' ', '_').upper()
                img_path = f"{img_name}.png"
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                else:
                    st.info("Kvalitné originálne príslušenstvo k posteliam FINES.")

            st.write("---")
            if st.button("Vložiť do košíka ➔", type="primary", use_container_width=True, key="btn_doplnok_cart"):
                st.session_state.kosik.append({
                    "typ": "Doplnok",
                    "nazov": f"{doplnok['kod']}",
                    "doplnok": doplnok,
                    "cena": cena_doplnok
                })
                st.session_state.current_tab = "📋 2. Košík"
                st.rerun()

