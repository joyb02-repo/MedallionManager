import streamlit as st
import requests
import os
import base64
import random
import time

API_URL = st.secrets["API_URL"]

if "username" not in st.session_state:
    st.session_state["username"] = "joyb02"

# Keep track of mining states in native Python session state
if "mined_item" not in st.session_state:
    st.session_state["mined_item"] = None
if "is_saving" not in st.session_state:
    st.session_state["is_saving"] = False

MEDALLION_COLUMNS = [
    "Spruce", "Pine", "Meranti", "Balsa", "Oak", "Maple", 
    "Walnut", "Cherry", "Mahogany", "Ebony", "Rosewood", "Agarwood"
]

st.set_page_config(page_title="Timber Medallion Portfolio", layout="wide")

# ====================================================================
# PHASE 1: BACKEND POST HANDLING (Executed purely in Python)
# ====================================================================
def process_claim_to_google_sheets(item_name):
    try:
        payload = {
            "action": "mineMedallion", 
            "item": item_name, 
            "username": st.session_state["username"]
        }
        res = requests.post(API_URL, json=payload, timeout=15)
        if res.status_code == 200:
            st.cache_data.clear()
            st.session_state["mined_item"] = None
            st.session_state["is_saving"] = False
            st.rerun()
    except Exception as e:
        st.error(f"Failed to record mined item to cloud sheet: {e}")
        st.session_state["is_saving"] = False

@st.cache_data(ttl=1)
def fetch_all_sheet_data(user_id):
    try:
        payload = {"action": "fetchData", "username": user_id}
        response = requests.post(API_URL, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                medallions_map = {str(m["Medallion"]).strip().lower(): m for m in data.get("medallions", [])}
                master_summary = data.get("master_summary", {})
                
                inventory_counts = master_summary.get("Inventory", {})
                val = master_summary.get("CollectionValue", "$0")
                coll = master_summary.get("MedallionsCollected", "0")
                
                return medallions_map, inventory_counts, val, coll
    except Exception as e:
        st.error(f"Sync Failure: {str(e)}")
    return {}, {}, "Loading...", "Loading..."

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

live_data, live_inventory, summary_value, summary_collected = fetch_all_sheet_data(st.session_state["username"])

if not summary_value.strip().startswith("$") and "Loading" not in summary_value:
    summary_value = f"${summary_value.strip()}"

asset_map_js = "{"
for wood in MEDALLION_COLUMNS:
    b64 = get_image_base64(f"assets/{wood.lower()}.png")
    if b64:
        asset_map_js += f"'{wood}': 'data:image/png;base64,{b64}',"
asset_map_js += "}"

# ====================================================================
# HTML/CSS PORTFOLIO DISPLAY
# ====================================================================
html_base_template = """
<style>
    body {
        margin: 0; padding: 50px 0 0 0; background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px; font-family: 'Inter', system-ui, sans-serif;
    }
    .portfolio-title { text-align: center; font-size: 24px; font-weight: 600; color: #FFFFFF; margin-bottom: 12px; }
    .portfolio-intro { text-align: center; max-width: 800px; margin: 0 auto 50px auto; font-size: 13px; line-height: 1.6; color: rgba(255, 255, 255, 0.25); }
    .portfolio-intro span { color: rgba(244, 208, 104, 0.4); font-weight: 600; }
    .casement-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px; padding: 0 15px; }
    .grid-node { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    .image-frame { width: 62px; height: 62px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; }
    .image-frame img, .lock-node { width: 100%; height: 100%; object-fit: contain; transition: transform 0.15s ease-in-out; }
    .lock-node { width: 52px; height: 52px; border-radius: 50%; border: 2px dashed #23273A; background: #161925; display: flex; align-items: center; justify-content: center; color: #3D4563; font-size: 13px; }
    .grid-node:hover .image-frame img, .grid-node:hover .lock-node { transform: scale(1.15); }
    .quantity-badge { font-size: 12px; font-weight: 700; color: #F4D068; margin-bottom: 3px; min-height: 15px; }
    .label-badge { font-size: 10px; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }
    .node-tooltip { visibility: hidden; opacity: 0; position: absolute; top: -120px; left: 50%; transform: translateX(-50%); width: 180px; background: #161925; border: 1px solid #282E48; border-radius: 8px; padding: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.6); z-index: 99999; transition: opacity 0.12s ease-in-out; pointer-events: none; }
    .grid-node:hover .node-tooltip { visibility: visible; opacity: 1; }
    .grid-node:first-child .node-tooltip { left: 0; transform: translateX(0); }
    .grid-node:last-child .node-tooltip { left: auto; right: 0; transform: translateX(0); }
    .tip-line { font-size: 11px; color: #E2E8F0; margin-bottom: 5px; text-align: left; white-space: nowrap; }
    .tip-line span { font-weight: 700; color: #F4D068; }
    .tip-line span.rarity-common { color: #CD7F32; }       
    .tip-line span.rarity-uncommon { color: #C0C0C0; }     
    .tip-line span.rarity-rare { color: #3b82f6; }         
    .tip-line span.rarity-epic { color: #a855f7; }         
    .tip-line span.rarity-legendary { color: #f59e0b; }    
    .dashboard-row { display: flex; justify-content: center; gap: 20px; margin-top: 45px; padding: 0 15px; }
    .stat-card { background: #161925; border: 1px solid #23273A; border-radius: 6px; padding: 10px 20px; min-width: 180px; text-align: center; }
    .stat-label { font-size: 11px; text-transform: uppercase; color: #718096; letter-spacing: 0.75px; margin-bottom: 4px; }
    .stat-value { font-size: 18px; font-weight: 700; color: #FFF; }
</style>

<div class="portfolio-title">Timber Medallion Portfolio</div>
<div class="portfolio-intro"> Master tracking dashboard powered directly by your cloud inventory records. Premium tokens scale in rarity up to the single production run <span>Agarwood Medallion</span>.</div>

<div class="casement-grid">
__GRID_ITEMS_PLACEHOLDER__
</div>

<div class="dashboard-row">
    <div class="stat-card">
        <div class="stat-label">Collection Value</div>
        <div class="stat-value">__VALUE_PLACEHOLDER__</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Medallions Collected</div>
        <div class="stat-value">__COLLECTED_PLACEHOLDER__</div>
    </div>
</div>
"""

grid_elements_html = ""
for wood_name in MEDALLION_COLUMNS:
    display_label = wood_name[:5].upper()
    lookup_key = wood_name.strip().lower()
    
    owned = int(live_inventory.get(lookup_key, 0))
    sheet_row = live_data.get(lookup_key, None)
    rarity_class = ""
    
    if sheet_row:
        rarity = sheet_row.get("Rarity", "N/A")
        value = sheet_row.get("Value", "N/A")
        availability = sheet_row.get("Availability", "N/A")
        probability = sheet_row.get("Probability", "N/A")
        
        clean_rarity = str(rarity).strip().lower()
        if "common" in clean_rarity and "uncommon" not in clean_rarity: rarity_class = "rarity-common"
        elif "uncommon" in clean_rarity: rarity_class = "rarity-uncommon"
        elif "rare" in clean_rarity: rarity_class = "rarity-rare"
        elif "epic" in clean_rarity: rarity_class = "rarity-epic"
        elif "legendary" in clean_rarity: rarity_class = "rarity-legendary"
        
        if value != "N/A" and not str(value).strip().startswith("$"): value = f"${str(value).strip()}"
        if probability != "N/A" and not str(probability).endswith("%"): probability = f"{probability}%"
    else:
        rarity = value = availability = probability = "Loading..."
        
    img_b64 = get_image_base64(f"assets/{wood_name.lower()}.png")
    
    grid_elements_html += f"""
    <div class="grid-node">
        <div class="node-tooltip">
            <div class="tip-line">Name: <span>{wood_name}</span></div>
            <div class="tip-line">Rarity: <span class="{rarity_class}">{rarity}</span></div>
            <div class="tip-line">Value: <span>{value}</span></div>
            <div class="tip-line">Availability: <span>{availability} left</span></div>
            <div class="tip-line">Probability: <span>{probability}</span></div>
        </div>
        
        <div class="image-frame">
            {"<img src='data:image/png;base64," + img_b64 + "' />" if (owned > 0 and img_b64) else "<div class='lock-node'>🔒</div>"}
        </div>
        <div class="quantity-badge">{"x" + str(owned) if owned > 0 else "&nbsp;"}</div>
        <div class="label-badge">{display_label}</div>
    </div>
    """

html_elements = html_base_template.replace("__GRID_ITEMS_PLACEHOLDER__", grid_elements_html)
html_elements = html_elements.replace("__VALUE_PLACEHOLDER__", summary_value)
html_elements = html_elements.replace("__COLLECTED_PLACEHOLDER__", summary_collected)

# Render main grid and stats
st.components.v1.html(html_elements, height=420, scrolling=False)


# ====================================================================
# PHASE 2: NATIVE STREAMLIT MINING CONTROLS (Bypasses all iframe limits)
# ====================================================================
st.markdown("""
<style>
    /* Synchronize centering layouts matching original design specs */
    .element-container, .stButton { display: flex; justify-content: center; width: 100%; }
    div[data-testid="stVerticalBlock"] > div { display: flex; flex-direction: column; align-items: center; }
    
    /* Native button override injecting original visual token parameters */
    div.stButton > button {
        width: 424px !important; height: 46px !important; 
        background-color: #F4D068 !important; border: none !important; color: #0E1117 !important;
        font-size: 14px !important; font-weight: 700 !important; text-transform: uppercase !important;
        box-shadow: 0 4px 15px rgba(244, 208, 104, 0.2) !important; border-radius: 6px !important;
        transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    div.stButton > button:hover { transform: scale(1.05) !important; color: #0E1117 !important; }
    div.stButton > button:disabled { opacity: 0.6 !important; background-color: #23273A !important; color: #718096 !important; }
</style>
""", unsafe_allow_html=True)

# Main action logic triggers selector state updates natively
if not st.session_state["mined_item"] and not st.session_state["is_saving"]:
    if st.button("Mine a Medallion", key="mine_action_trigger"):
        st.session_state["mined_item"] = random.choice(MEDALLION_COLUMNS)
        st.rerun()

# Execute layout frame if user holds a temporary token claim state
if st.session_state["mined_item"]:
    item_won = st.session_state["mined_item"]
    img_b64_won = get_image_base64(f"assets/{item_won.lower()}.png")
    
    animation_iframe_template = """
    <style>
        body { margin: 0; background: transparent; display: flex; flex-direction: column; align-items: center; font-family: 'Inter', sans-serif; }
        .spin-box { width: 140px; height: 140px; border-radius: 12px; background: #161925; border: 3px solid #23273A; display: flex; align-items: center; justify-content: center; box-sizing: border-box; }
        .spin-box img { width: 88%; height: 88%; object-fit: contain; }
        .outcome-text-wrapper { margin-top: 15px; text-align: center; }
        .outcome-top { font-size: 11px; font-weight: 600; color: #718096; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px; }
        .outcome-bottom { font-size: 18px; font-weight: 800; color: #F4D068; text-transform: uppercase; }
    </style>
    <div class="spin-box" id="cyclerBox">
        <img id="cyclerImg" src="" />
    </div>
    <div class="outcome-text-wrapper" id="outcomeWrapper" style="opacity: 0;">
        <div class="outcome-top">Successfully Mined:</div>
        <div class="outcome-bottom">__WIN_NAME__ MEDALLION!</div>
    </div>
    <script>
        const assetLibrary = __ASSET_MAP__;
        const pool = ['Spruce', 'Pine', 'Meranti', 'Balsa', 'Oak', 'Maple', 'Walnut', 'Cherry', 'Mahogany', 'Ebony', 'Rosewood', 'Agarwood'];
        const target = "__WIN_NAME__";
        const img = document.getElementById('cyclerImg');
        const wrapper = document.getElementById('outcomeWrapper');
        
        let counter = 0;
        let speed = 40;

        function cycle() {
            const currentItem = pool[counter % pool.length];
            if (assetLibrary[currentItem]) img.src = assetLibrary[currentItem];
            counter++;

            if (speed < 260) {
                speed += 14;
                setTimeout(cycle, speed);
            } else {
                if (assetLibrary[target]) img.src = assetLibrary[target];
                wrapper.style.opacity = "1";
            }
        }
        cycle();
    </script>
    """
    anim_html = animation_iframe_template.replace("__WIN_NAME__", item_won).replace("__ASSET_MAP__", asset_map_js)
    
    # Render animated box element
    st.components.v1.html(anim_html, height=210, scrolling=False)
    
    # Submitting claim uses native Python processing logic bypassing network cross-origin bars
    if not st.session_state["is_saving"]:
        if st.button(f"Claim {item_won} Medallion", key="claim_action_trigger"):
            st.session_state["is_saving"] = True
            st.rerun()
else:
    if st.session_state["is_saving"]:
        # Show processing load-state cleanly
        st.markdown(
            "<div style='text-align:center; color:#F4D068; font-weight:700; margin-top:20px; font-size:14px; text-transform:uppercase; letter-spacing:1px;'>Saving to Cloud Sheet...</div>", 
            unsafe_allow_html=True
        )
        process_claim_to_google_sheets(st.session_state["mined_item"])
