import streamlit as st
import os

def render_rosty(data_rosty):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🪵 Konfigurátor roštu (MOC Cenník)")
    
    if not data_rosty:
        st.warning("Nenašli sa žiadne rošty. Spusť skript `generate_rosty.py` pre vygenerovanie `program_rosty.xlsx`.")
    else:
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            vybrany_rost_idx = st.selectbox(
                "Výber roštu:", 
                range(len(data_rosty)), 
                format_func=lambda i: f"{data_rosty[i]['kod']} (Šírka: {data_rosty[i]['sirka']})"
            )
            rost = data_rosty[vybrany_rost_idx]
            
            typ_ceny = st.radio("Typ MOC ceny:", ["Cena MOC s DPH", "Akciová MOC cena (-30%)"])
            cena_rostu = rost['cena_moc_akcia'] if typ_ceny == "Akciová MOC cena (-30%)" else rost['cena_moc']
            
            st.markdown(f"**Šírka:** {rost['sirka']}")
            st.markdown(f"**Nosnosť:** {rost['nosnost']}")
            st.metric("Cena roštu:", f"{cena_rostu:.2f} €", f"{typ_ceny}")
            
        with col_r2:
            st.markdown("**Detail roštu / Náhľad ponuky**")
            img_map = {
                "MASÍV - zvinovací rošt": "rosty_img/page_2_max.png",
                "MASÍV v ráme": "rosty_img/page_3_max.png",
                "Double KLASIK PNEU BV lam.35 (bočný výkl.)": "rosty_img/page_4_max.png",
                "Double KLASIK PNEU PV lam.35 (predný výkl.)": "rosty_img/page_5_max.png",
                "MASÍV v ráme PNEU BV (bočný výklop)": "rosty_img/page_6_max.png",
                "MASÍV v ráme PNEU PV (predný výklop)": "rosty_img/page_7_max.png",
                "PERFEKT": "rosty_img/page_8_max.png",
                "PERFEKT PLUS": "rosty_img/page_9_max.png",
                "PERFEKT PLUS 5V": "rosty_img/page_10_max.png",
                "Double EXPERT PNEU polohovací PV, lam. 35": "rosty_img/page_11_max.png"
            }
            img_path = img_map.get(rost['kod'])
            if img_path and os.path.exists(img_path):
                st.image(img_path, caption=rost['kod'], use_container_width=True)
            else:
                st.info("Náhľad roštu zo zoznamu katalógu (strana 28 katalógu postelí)")

        st.write("---")
        if st.button("Vložiť do košíka ➔", type="primary", use_container_width=True, key="btn_slat_cart"):
            st.session_state.kosik.append({
                "typ": "Rošt",
                "nazov": f"Rošt {rost['kod']} ({rost['sirka']})",
                "rost": rost,
                "cena": cena_rostu,
                "img_path": img_path
            })
            st.session_state.current_tab = "📋 2. Košík"
            st.rerun()

