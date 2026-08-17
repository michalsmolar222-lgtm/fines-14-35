import streamlit as st
import os

def render_masiv(data_masiv, data_ulozne):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🌲 Konfigurátor drevených postelí a nábytku z masívu")
    
    if not data_masiv:
        st.warning("Nenašli sa žiadne produkty z masívu. Spusť skript `generate_masiv.py` pre vygenerovanie `program_masiv.xlsx`.")
    else:
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            def get_masiv_base_name(kod):
                kod = str(kod).strip()
                if kod.startswith("MATE LUX"): return "MATE LUX"
                if kod.startswith("MATE"): return "MATE"
                if kod.startswith("LIBORA"): return "LIBORA"
                if kod.startswith("KARS"): return "KARS"
                if kod.startswith("TALIA"): return "TALIA"
                if kod.startswith("MONAKO"): return "MONAKO"
                if kod.startswith("TINA"): return "TINA"
                return kod
            
            # Zoskupenie podla base_name
            masiv_by_base = {}
            for idx, item in enumerate(data_masiv):
                base = get_masiv_base_name(item['kod'])
                if base not in masiv_by_base:
                    masiv_by_base[base] = []
                masiv_by_base[base].append((idx, item))
            
            base_names = list(masiv_by_base.keys())
            
            default_base_idx = 0
            edit_item = st.session_state.get('edit_item')
            if edit_item and edit_item['typ'] == "Drevená posteľ":
                base_kod = get_masiv_base_name(edit_item['masiv']['kod'])
                if base_kod in base_names:
                    default_base_idx = base_names.index(base_kod)
            
            vybrany_base = st.selectbox("1. Názov postele:", base_names, index=default_base_idx)
            
            variants_for_base = masiv_by_base[vybrany_base]
            
            def format_masiv_variant(variant_tuple):
                idx, item = variant_tuple
                suffix = str(item['kod']).replace(vybrany_base, "").strip()
                desc = f"{suffix} - {item['popis']}" if suffix else item['popis']
                return desc
            
            default_variant_idx = 0
            if edit_item and edit_item['typ'] == "Drevená posteľ":
                for i, v in enumerate(variants_for_base):
                    if v[1]['kod'] == edit_item['masiv']['kod']:
                        default_variant_idx = i
                        break
                        
            vybrany_variant_tuple = st.selectbox(
                "2. Typ postele a spacieho systému:",
                variants_for_base,
                format_func=format_masiv_variant,
                index=default_variant_idx
            )
            
            vybrany_masiv_idx = vybrany_variant_tuple[0]
            masiv_item = vybrany_variant_tuple[1]
            
            drevo_options = ["Buk prírodný", "Buk morený / farebný", "Dub"]
            default_drevo_idx = 0
            if edit_item and edit_item['typ'] == "Drevená posteľ":
                provedenie_str = edit_item.get('provedenie', '')
                for i, opt in enumerate(drevo_options):
                    if opt in provedenie_str:
                        default_drevo_idx = i
                        break
                        
            provozuvanie = st.radio(
                "3. Prevedenie dreva / povrchová úprava:",
                drevo_options,
                index=default_drevo_idx
            )
            
            if provozuvanie == "Buk prírodný":
                cena_masiv = masiv_item['buk_prirodny']
            elif provozuvanie == "Buk morený / farebný":
                cena_masiv = masiv_item['buk_moreny']
            else:
                cena_masiv = masiv_item['dub_farebny']
            
            ulozny_options = [{"Kod": "Žiadny", "Popis": "Bez úložného priestoru"}] + data_ulozne
            
            default_ulozny_idx = 0
            if edit_item and edit_item['typ'] == "Drevená posteľ":
                provedenie_str = edit_item.get('provedenie', '')
                for i, opt in enumerate(ulozny_options):
                    if opt['Kod'] != 'Žiadny' and f"[+ {opt['Kod']}]" in provedenie_str:
                        default_ulozny_idx = i
                        break
                        
            vybrany_ulozny = st.selectbox(
                "4. Možnosti úložného priestoru:",
                ulozny_options,
                format_func=lambda x: f"{x['Kod']} - {x['Popis']}" if x['Kod'] != 'Žiadny' else x['Popis'],
                index=default_ulozny_idx
            )
            
            if vybrany_ulozny['Kod'] != 'Žiadny':
                if provozuvanie == "Buk prírodný":
                    cena_masiv += vybrany_ulozny['Buk_Prirodny']
                elif provozuvanie == "Buk morený / farebný":
                    cena_masiv += vybrany_ulozny['Buk_Moreny']
                else:
                    cena_masiv += vybrany_ulozny['Dub_Farebny']
                provozuvanie += f" [+ {vybrany_ulozny['Kod']}]"
                
            st.markdown(f"**Popis:** {masiv_item['popis']}")
            
            vybrana_sirka_masiv = str(masiv_item['sirka']).strip()
            if masiv_item['sirka']:
                if "180" in str(masiv_item['sirka']) and "160" in str(masiv_item['sirka']):
                    default_sirka_idx = 0
                    if edit_item and edit_item['typ'] == "Drevená posteľ":
                        provedenie_str = edit_item.get('provedenie', '')
                        if "[Šírka: 160 cm]" in provedenie_str:
                            default_sirka_idx = 1
                    vybrana_sirka_masiv = st.radio("Šírka postele:", ["180 cm", "160 cm"], horizontal=True, index=default_sirka_idx)
                else:
                    st.markdown(f"**Šírka / Rozmer:** {masiv_item['sirka']}")
                    
            if vybrana_sirka_masiv:
                provozuvanie += f" [Šírka: {vybrana_sirka_masiv}]"
                
            default_atyp_val = False
            default_atyp_dlzka_idx = 0
            if edit_item and edit_item['typ'] == "Drevená posteľ":
                provedenie_str = edit_item.get('provedenie', '')
                if "ATYP Predĺžená na" in provedenie_str:
                    default_atyp_val = True
                    if "220 cm" in provedenie_str:
                        default_atyp_dlzka_idx = 1
                        
            atyp_m = st.checkbox("Predĺžená dĺžka postele (ATYP + 20 %)", key="atyp_m", value=default_atyp_val)
            if atyp_m:
                cena_masiv = cena_masiv * 1.20
                atyp_dlzka_m = st.selectbox("Požadovaná dĺžka:", ["210 cm", "220 cm"], key="atyp_dlzka_m", index=default_atyp_dlzka_idx)
                provozuvanie = provozuvanie + f" [ATYP Predĺžená na {atyp_dlzka_m}]"
                
            st.metric("Cena s DPH:", f"{cena_masiv:.2f} €", f"{provozuvanie}")
            
        with col_m2:
            st.markdown("**Náhľad a parametre**")
            import os
            img_name = str(masiv_item['kod']).replace('/', '_').replace(' ', '_').upper()
            img_path = f"{img_name}.png"
            base_img_name = vybrany_base.replace('/', '_').replace(' ', '_').upper()
            base_img_path = f"{base_img_name}.png"
            
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            elif os.path.exists(base_img_path):
                st.image(base_img_path, use_container_width=True)
            else:
                st.info("Kvalitné slovenské drevené postele a príslušenstvo vyrobené z masívneho buku a dubu.")

        st.write("---")

        st.write("---")
        if st.button("Vložiť do košíka ➔", type="primary", use_container_width=True, key="btn_masiv_cart"):
            st.session_state.kosik.append({
                "typ": "Drevená posteľ",
                "nazov": f"{masiv_item['kod']} ({provozuvanie})",
                "masiv": masiv_item,
                "provedenie": provozuvanie,
                "cena": cena_masiv
            })
            st.session_state.current_tab = "📋 2. Košík"
            st.rerun()

