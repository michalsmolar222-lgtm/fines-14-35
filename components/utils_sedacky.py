import math
import urllib.parse
import streamlit as st
ROZMERY_VSETKY = {
    "MARVEL": {"1": (97, 89), "OTP/OTL": (198, 89), "2P": (167, 89), "3P": (233, 89), "3R": (233, 89), "DU-": (86, 158), "DM-": (89, 115), "DRO-": (89, 200), "ROH": (86, 86), "-2SP-": (131, 89), "-2SR-": (131, 89), "-3SP-": (197, 89), "-3SR-": (197, 89), "B2P-": (149, 89), "B2R-": (149, 89), "B3P-": (215, 89), "B3R-": (215, 89), "T": (68, 54)},
    "MISTRAL": {"1": (97, 89), "OTP/OTL": (198, 89), "2P": (167, 89), "3P": (233, 89), "3R": (233, 89), "DU-": (86, 158), "DM-": (89, 115), "DRO-": (89, 200), "ROH": (86, 86), "-2SP-": (131, 89), "-2SR-": (131, 89), "-3SP-": (197, 89), "-3SR-": (197, 89), "B2P-": (149, 89), "B2R-": (149, 89), "B3P-": (215, 89), "B3R-": (215, 89), "T": (68, 54)},
    "RENDY": {"1": (95, 84), "2P": (168, 84), "2U": (168, 84), "3P": (231, 84), "3U": (231, 84), "3R": (231, 84), "B1-": (77, 84), "B2P-": (150, 84), "B2U-": (150, 84), "B2R-": (150, 84), "B3P-": (213, 84), "B3U-": (213, 84), "B3R-": (213, 84), "-3SP-": (195, 84), "-3SU-": (195, 84), "-3SR-": (195, 84), "-2SP-": (132, 84), "-2SU-": (132, 84), "-2SR-": (132, 84), "-1S-": (59, 84), "ROH": (84, 84), "DU-": (56, 163), "DM-": (86, 100), "TAB": (68, 49)},
    "FAMILY": {"B3R160-": (200, 212), "B3R140-": (180, 212), "-3R160-": (179, 212), "-3R140-": (159, 212), "DRM-": (103, 203), "DRO-": (103, 203), "DU-": (103, 156), "PODHL.RA": (50, 20), "PODHL.RB": (50, 20)},
    "SIONE LIGHT": {"B1-": (111, 102), "-1S-": (75, 102), "ROH": (102, 102), "2P": (201, 102), "B2P-": (165, 102), "-2SP-": (129, 102), "2,5P": (222, 102), "B2,5P-": (186, 102), "-2,5SP-": (150, 102), "DU-": (113, 180), "DM": (102, 132), "LTI TAB": (113, 78), "VTL TAB": (125, 73), "STL TAB": (76, 66)},
    "SIONE": {"B1-": (111, 102), "-1S-": (75, 102), "ROH": (102, 102), "2P": (201, 102), "B2P-": (165, 102), "B2R-": (165, 102), "-2SP-": (129, 102), "-2SR-": (129, 102), "2,5P": (222, 102), "B2,5P-": (186, 102), "B2,5R-": (186, 102), "-2,5SP-": (150, 102), "-2,5SR-": (150, 102), "DU-": (113, 180), "DM": (102, 132), "TAB MALÁ": (78, 66), "VT VEĽKÁ": (125, 72)},
    "SABRINA": {"1": (104, 95), "B1-": (82, 95), "-1S-": (61, 95), "2U": (148, 95), "B2U-": (125, 95), "-2SU-": (102, 95), "3P": (199, 95), "3R": (199, 95), "3U": (199, 95), "B3P-": (176, 95), "B3U-": (176, 95), "B3RM-": (176, 95), "B3RV-": (176, 95), "-3SP-": (153, 95), "-3SU-": (153, 95), "-3SRM-": (153, 95), "-3SRV-": (153, 95), "ROH": (90, 90), "VROH": (103, 103), "DU": (91, 158), "DUK": (91, 158), "PT": (91, 60), "TAB": (52, 52), "PH": (76, 51), "VT": (91, 60)},
    "SARAH": {"1": (104, 95), "B1-": (82, 95), "-1S-": (61, 95), "2U": (148, 95), "B2U-": (125, 95), "-2SU-": (102, 95), "3P": (199, 95), "3R": (199, 95), "3U": (199, 95), "B3P-": (176, 95), "B3U-": (176, 95), "B3RM-": (176, 95), "B3RV-": (176, 95), "-3SP-": (153, 95), "-3SU-": (153, 95), "-3SRM-": (153, 95), "-3SRV-": (153, 95), "ROH": (90, 90), "VROH": (103, 103), "DU": (91, 158), "DUK": (91, 158), "PT": (91, 60), "TAB": (52, 52), "PH": (76, 51), "VT": (91, 60)},
    "GENEZA": {"1": (102, 88), "B1-": (95, 88), "-1S-": (74, 88), "2P": (189, 88), "2R": (189, 88), "B2P-": (167, 88), "B2RM-": (167, 88), "B2RV-": (167, 88), "-2SP-": (147, 88), "-2SRM-": (147, 88), "-2SRV-": (147, 88), "3P": (260, 88), "3R": (260, 88), "B3P-": (240, 88), "B3R-": (240, 88), "-3SP-": (218, 88), "-3SR-": (218, 88), "DU": (94, 147), "DRM": (102, 202), "DM": (110, 88), "P": (71, 88), "PN": (61, 56), "BDF": (133, 129), "DF": (117, 129), "ROS": (106, 106), "ROH": (84, 84)},
    "EGO": {"1M": (112, 96), "B1M-": (86, 96), "-1SM-": (60, 96), "1V": (150, 96), "B1V-": (124, 96), "-1SV-": (98, 96), "2P": (173, 96), "B2P-": (147, 96), "B2R-": (147, 96), "-2SR-": (121, 96), "3P": (243, 96), "3R": (243, 96), "B3P-": (217, 96), "B3R-": (217, 96), "DU-": (126, 163), "T": (96, 64), "VT": (122, 57)},
    "PARADISO": {"1": (108, 88), "B1-": (88, 88), "2P": (167, 88), "B2P-": (145, 88), "2,5P": (195, 88), "2,5R": (195, 88), "B2,5P-": (173, 88), "B2,5RM-": (173, 88), "B2,5RV-": (173, 88), "3P": (268, 88), "3R": (268, 88), "B3P-": (246, 88), "B3R-": (246, 88), "ROS": (106, 106), "ROH": (84, 84), "T": (56, 48)},
    "HESTIA": {"1": (100, 100), "B1-": (80, 100), "-1S-": (60, 100), "2U": (140, 100), "B2U-": (120, 100), "-2SU-": (100, 100), "3P": (192, 100), "3R": (192, 100), "B3P-": (172, 100), "B3RM-": (172, 100), "B3RV-": (172, 100), "-3SP-": (152, 100), "-3SRM-": (152, 100), "-3SRV-": (152, 100), "ROH": (94, 94), "PT": (91, 60), "VT": (91, 60), "DU": (87, 150), "TAB": (52, 48)},
    "KLAUDIA": {"1": (100, 100), "B1-": (80, 100), "-1S-": (60, 100), "2U": (140, 100), "B2U-": (120, 100), "-2SU-": (100, 100), "3P": (192, 100), "3R": (192, 100), "B3P-": (172, 100), "B3RM-": (172, 100), "B3RV-": (172, 100), "-3SP-": (152, 100), "-3SRM-": (152, 100), "-3SRV-": (152, 100), "ROH": (94, 94), "PT": (91, 60), "VT": (91, 60), "DU": (87, 150), "TAB": (52, 48)},
    "ADENA": {"1": (91, 94), "2": (142, 94), "3P": (196, 94), "3R": (196, 94)},
    "ELNINO": {"1": (91, 94), "2": (142, 94), "3P": (197, 94), "TAB": (62, 48)}
}

def get_rozmery(el_kod, m):
    if not m or not isinstance(m, str):
        return (100, 90)
    k = str(el_kod).strip().upper().replace(" ", "")
    if k == "-DM": k = "DM-"
    if k == "-ROH-": k = "ROH"
    
    for key_model in ROZMERY_VSETKY.keys():
        if key_model in m.upper():
            if k in ROZMERY_VSETKY[key_model]:
                return ROZMERY_VSETKY[key_model][k]
                
    return (100, 90)

def vytvor_skicu(kod, model="MARVEL", scale=1.3, mini=False, position="left", cx=None, cy=None, angle=0):
    if not model: model = "MARVEL"
    w, h = get_rozmery(kod, model)
    arm_w = 18; br = 21
    if model and "FAMILY" in str(model).upper():
        arm_w = 21; br = 25

    typ = "standard"
    armL, armR = 0, 0
    seats = 1
    
    kod_clean = kod.strip().upper().replace(" ", "")
    if kod_clean == "-DM": kod_clean = "DM-"
    if kod_clean == "-ROH-": kod_clean = "ROH"
    
    is_stredovy = kod_clean.startswith("-") and kod_clean.endswith("-")
    
    if kod_clean == "1": armL, armR, seats = arm_w, arm_w, 1
    elif kod_clean in ["2P", "2R", "2U"] or kod_clean.startswith("3P") or kod_clean.startswith("3R") or kod_clean.startswith("3U"): 
        armL, armR = arm_w, arm_w
        seats = 3 if "3" in kod_clean else 2
    elif kod_clean.startswith("B2") or kod_clean.startswith("B1"): 
        armL, armR, seats = arm_w, 0, 2 if "2" in kod_clean else 1
    elif kod_clean.startswith("B3"): 
        armL, armR, seats = arm_w, 0, 3
    elif is_stredovy:
        if "3" in kod_clean: seats = 3
        elif "2" in kod_clean: seats = 2
    elif "DU" in kod_clean or "DM" in kod_clean: armL, armR, typ = arm_w, 0, "chaiselongue"
    elif "DRO" in kod_clean or "DRM" in kod_clean: typ = "dro"
    elif "ROH" in kod_clean: typ = "corner"
    elif "OT" in kod_clean: armL, armR, seats = arm_w, arm_w, 3 
    elif "TAB" in kod_clean or "T" == kod_clean or "PODHL" in kod_clean: typ = "poufe"
    
    if position == "right":
        armL, armR = armR, armL
    
    W, H = w * scale, h * scale
    AL, AR, BR = armL * scale, armR * scale, br * scale
    
    if cx is not None and cy is not None:
        left = cx - W/2
        top = cy - H/2
        pos_style = f"position: absolute; left: {left}px; top: {top}px; transform: rotate({angle}deg); transform-origin: center center; z-index: 5;"
    else:
        margin_right = "0px" if mini else "-2px"
        pos_style = f"position: relative; margin-right: {margin_right}; flex-shrink: 0;"
        
    html = f'<div style="width: {W}px; height: {H}px; border: 2px solid #1e293b; background: #fff; box-sizing: border-box; overflow: hidden; {pos_style}">'
    
    if typ == "standard":
        if armL > 0: html += f'<div style="position: absolute; top: 0; bottom: 0; left: {AL}px; border-left: 2px solid #1e293b;"></div>'
        if armR > 0: html += f'<div style="position: absolute; top: 0; bottom: 0; right: {AR}px; border-right: 2px solid #1e293b;"></div>'
        if br > 0: html += f'<div style="position: absolute; top: {BR}px; left: {AL}px; right: {AR}px; border-top: 2px solid #1e293b;"></div>'
        if seats > 1:
            seat_w = (w - armL - armR) / seats * scale
            for i in range(1, seats):
                pos = AL + i * seat_w
                html += f'<div style="position: absolute; top: {BR}px; bottom: 0; left: {pos}px; border-left: 2px solid #1e293b;"></div>'
                
    elif typ == "chaiselongue":
        html += f'<div style="position: absolute; top: {BR}px; left: 0; right: 0; border-top: 2px solid #1e293b;"></div>'
        html += f'<div style="position: absolute; top: {89 * scale}px; left: 0; right: 0; border-top: 2px solid #1e293b;"></div>'
        if armL > 0: html += f'<div style="position: absolute; top: 0; bottom: 0; left: {AL}px; border-left: 2px solid #1e293b;"></div>'
        if armR > 0: html += f'<div style="position: absolute; top: 0; bottom: 0; right: {AR}px; border-right: 2px solid #1e293b;"></div>'
        
    elif typ == "dro":
        html += f'<div style="position: absolute; top: {89 * scale}px; left: 0; right: 0; border-top: 2px solid #1e293b;"></div>'
        if position != "right":
            html += f'<div style="position: absolute; top: {BR}px; left: {BR}px; right: 0; border-top: 2px solid #1e293b;"></div>'
            html += f'<div style="position: absolute; top: 0; height: {89 * scale}px; left: {BR}px; border-left: 2px solid #1e293b;"></div>'
        else:
            html += f'<div style="position: absolute; top: {BR}px; left: 0; right: {BR}px; border-top: 2px solid #1e293b;"></div>'
            html += f'<div style="position: absolute; top: 0; height: {89 * scale}px; right: {BR}px; border-right: 2px solid #1e293b;"></div>'
            
    elif typ == "corner":
        # Kreslíme roh vždy konzistentne (napr. opierka hore a vpravo), aby sa vizuálne nepretáčal pri pridaní ďalšieho dielu.
        # Ak ho používateľ chce otočiť inak, môže na to využiť novú roletku Rotácia.
        html += f'<div style="position: absolute; top: {BR}px; left: 0; right: {BR}px; border-top: 2px solid #1e293b;"></div>'
        html += f'<div style="position: absolute; top: {BR}px; bottom: 0; right: {BR}px; border-right: 2px solid #1e293b;"></div>'
    
    if not mini:
        html += f'<div style="position: absolute; top: 2px; width: 100%; text-align: center; z-index: 10;"><span style="display: inline-block; transform: rotate({-angle}deg); font-size: 12px; color: #dc2626; font-weight: bold; background: rgba(255,255,255,0.85); padding: 0 4px; border-radius: 3px;">{w}</span></div>'
        html += f'<div style="position: absolute; left: 2px; top: 50%; transform: translateY(-50%); z-index: 10;"><div style="display: inline-block; transform: rotate({-angle}deg);"><span style="font-size: 12px; color: #dc2626; font-weight: bold; background: rgba(255,255,255,0.85); padding: 2px; border-radius: 3px;">{h}</span></div></div>'
        html += f'<div style="position: absolute; bottom: 8px; width: 100%; text-align: center; z-index: 10;"><span style="display: inline-block; transform: rotate({-angle}deg); font-size: 13px; font-weight: 900; color: #2563eb; text-shadow: 1px 1px 3px white;">{kod}</span></div>'
    else:
        html += f'<div style="position: absolute; top: 2px; width: 100%; text-align: center; font-size: 10px; color: #64748b; font-weight: bold; background: rgba(255,255,255,0.7);">{w}x{h}</div>'
        html += f'<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -40%); z-index: 10;"><div style="display: inline-block; transform: rotate({-angle}deg);"><span style="font-size: 12px; font-weight: 900; color: #2563eb; text-shadow: 1px 1px 2px white;">{kod}</span></div></div>'
        
    html += '</div>'
    return html

def get_max_connections(kod):
    k = kod.upper().strip().replace(" ", "")
    # Špeciálne výnimky pre rohy a otomany, ktoré nemusia mať vždy pomlčky v kóde
    if "ROH" in k or "ROS" in k: return 2
    if "OT" in k: return 1
    if k == "B2R": return 1 # preklep v Exceli pre niektoré modely
    if "TAB" in k or "PODHL" in k: return 0 # doplnky
    
    dashes = 0
    if k.startswith("-"): dashes += 1
    if k.endswith("-"): dashes += 1
    return dashes

def over_validitu_zostavy(aktualny_rad, novy_kod):
    if not aktualny_rad:
        return True, ""
        
    simulated = [el['kod'] for el in aktualny_rad] + [novy_kod]
    n = len(simulated)
    
    for i in range(n):
        k = simulated[i]
        max_c = get_max_connections(k)
        
        actual_c = 0
        if i > 0: actual_c += 1 # má spojenie doľava
        if i < n - 1: actual_c += 1 # má spojenie doprava
        
        if actual_c > max_c:
            return False, k
            
    return True, ""

