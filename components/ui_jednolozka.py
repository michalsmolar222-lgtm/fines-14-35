import streamlit as st
import os

def render_jednolozka(data_jednolozka, kategoria_látky):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🛏️ Konfigurátor jednolôžok a váľand")
    
    if not data_jednolozka:
        st.warning("Nenašli sa žiadne jednolôžka. Spusť skript `generate_jednolozka.py`.")
    else:
        kat_jl = st.selectbox("Kategória:", list(data_jednolozka.keys()))
        jl_list = data_jednolozka.get(kat_jl, [])
        
        if jl_list:
            col_jl1, col_jl2 = st.columns([1, 1])
            with col_jl1:
                vybrana_jl_idx = st.selectbox(
                    "Výber položky:",
                    range(len(jl_list)),
                    format_func=lambda i: f"{jl_list[i]['kod']} ({jl_list[i][kategoria_látky]} €) - {jl_list[i]['popis']}"
                )
                jl_item = jl_list[vybrana_jl_idx]
                
                if jl_item.get('cena_mix', 0) > 0:
                    volba_latky_jl = st.radio("Výber látky:", [f"Kategória látky ({kategoria_látky.capitalize()})", "Mix látok Fines (Akciová cena)"])
                    if "Mix" in volba_latky_jl:
                        cena_jl = jl_item['cena_mix']
                    else:
                        cena_jl = jl_item[kategoria_látky]
                else:
                    cena_jl = jl_item[kategoria_látky]
                    
                st.markdown(f"**Model:** {jl_item['model']}")
                st.markdown(f"**Popis:** {jl_item['popis']}")
                if jl_item.get('sirka_info'):
                    st.markdown(f"**Rozmer:** {jl_item['sirka_info']}")
                st.metric("Cena s DPH:", f"{cena_jl:.2f} €")
                
            with col_jl2:
                import os
                kod_str = str(jl_item['kod']).replace('/', '_').replace(' ', '_').upper()
                model_str = str(jl_item['model']).replace('/', '_').replace(' ', '_').upper()
                base_str = model_str.split('_')[0].split(' ')[0]
                
                img_path = None
                for candidate in [f"{kod_str}.png", f"{model_str}.png", f"{base_str}.png", f"{jl_item['model'].upper()}.png"]:
                    if os.path.exists(candidate):
                        img_path = candidate
                        break
                        
                if img_path and os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                else:
                    st.info("Kvalitné slovenské váľandy a jednolôžka s veľkým úložným priestorom (str. 25).")

            st.write("---")
            if st.button("Vložiť do košíka ➔", type="primary", use_container_width=True, key="btn_jl_cart"):
                st.session_state.kosik.append({
                    "typ": "Jednolôžko / Váľanda",
                    "nazov": f"{jl_item['kod']}",
                    "jednolozko": jl_item,
                    "latka": kategoria_látky,
                    "cena": cena_jl
                })
                st.session_state.current_tab = "📋 2. Košík"
                st.rerun()

