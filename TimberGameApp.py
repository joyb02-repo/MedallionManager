import streamlit as st
import requests
import os
import base64

# --- SECURE APPS SCRIPT LINK ---
API_URL = st.secrets["API_URL"]

# Exact 12-medallion sequence matching your sheet rows
MEDALLION_COLUMNS = [
    "Spruce", "Pine", "Meranti", "Balsa", "Oak", "Maple", 
    "Walnut", "Cherry", "Mahogany", "Ebony", "Rosewood", "Agarwood"
]

st.set_page_config(page_title="Medallion Showcase", page_icon="🏅", layout="wide")

# --- FOOLPROOF COLUMN-MATCHING FETCH ENGINE ---
def load_perfect_metadata():
    """
    Fetches rows from the Google Sheet and strictly binds columns B, C, D, and E 
    regardless of how the Apps Script formats the JSON response keys.
    """
    try:
        response = requests.post(API_URL, json={"action": "fetchData"}, timeout=15)
        if response.status_code == 200:
            backend_res = response.json()
            meta_map = {}
            
            for item in backend_res.get("medallions", []):
                # APPROACH A: If Apps Script returns raw row lists [Col A, Col B, Col C, Col D, Col E]
                if isinstance(item, list) and len(item) >= 5:
                    raw_name = str(item[0]).strip()
                    rarity = str(item[1]).strip()       # Column B
                    value = str(item[2]).strip()        # Column C
                    availability = str(item[3]).strip() # Column D
                    probability = str(item[4]).strip()  # Column E
                
                # APPROACH B: If Apps Script returns dictionary objects
                elif isinstance(item, dict):
                    # Normalize keys to lowercase to avoid any mismatch text issues
                    c_item = {str(k).strip().lower(): v for k, v in item.items()}
                    
                    raw_name = item.get("Medallion") or item.get("medallion") or item.get("Name")
                    if not raw_name:
                        # Fallback to key index values if named headers are missing
                        raw_name = next((v for k, v in item.items() if k.lower() == "a"), None)
                    
                    raw_name = str(raw_name).strip() if raw_name else None
                    
                    rarity = c_item.get("rarity") or c_item.get("b") or "Common"
                    value = c_item.get("value") or c_item.get("asset price") or c_item.get("c") or "$0"
                    availability = c_item.get("availability") or c_item.get("d") or "0"
                    probability = c_item.get("probability") or c_item.get("e") or "0%"
                else:
                    continue
                
                if raw_name:
                    clean_name = raw_name.lower()
                    meta_map[clean_name] = {
                        "RealName": raw_name,
                        "Rarity": rarity,
                        "Value": value,
                        "Availability": availability,
                        "Probability": probability if "%" in probability else f"{probability}%"
                    }
            return meta_map
    except Exception as e:
        st.error(f"Google Sheet Data Sync Error: {str(e)}")
    return {}

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Load the verified sheet data
live_metadata = load_perfect_metadata()

# Active user stock inventory (Hook your dynamic session row database profile here)
mock_user = {
    "Spruce": 6, "Pine": 2, "Meranti": 0, "Balsa": 0, "Oak": 0, "Maple": 0,
    "Walnut": 0, "Cherry": 0, "Mahogany": 2, "Ebony": 0, "Rosewood": 1, "Agarwood": 0
}

# --- HEADER TITLE RENDER ---
st.markdown("""
    <h3 style='font-family: system-ui; font-weight: 700; color: #FFFFFF; margin-bottom: 25px; letter-spacing: -0.5px;'>MEDALLION SHOWCASE CASEMENT</h3>
""", unsafe_allow_html=True)

# ====================================================================
# SEAMLESS SINGLE-IFRAME GRID WITH HEADROOM FOR TOOLTIPS
# ====================================================================

html_elements = """
<style>
    body {
        margin: 0;
        padding: 0;
        background-color: #0E1117; /* Matches standard Streamlit dark canvas canvas seamlessly */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        overflow: hidden;
    }
    .casement-grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 12px;
        padding-top: 150px; /* Generates dedicated headroom inside the frame for tooltips to expand safely upward */
        padding-left: 8px;
        padding-right: 8px;
    }
    .grid-node {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .image-frame {
        width: 62px;
        height: 62px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 8px;
    }
    .image-frame img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    .lock-node {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        border: 2px dashed #23273A;
        background: #161925;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #3D4563;
        font-size: 13px;
    }
    .quantity-badge {
        font-size: 12px;
        font-weight: 700;
        color: #F4D068;
        margin-bottom: 3px;
        min-height: 15px;
    }
    .label-badge {
        font-size: 10px;
        font-weight: 700;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Absolute Floating Tooltip Card Engine */
    .node-tooltip {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        bottom: 105px; /* Floats safely clear of the medallion graphics */
        left: 50%;
        transform: translateX(-50%);
        width: 165px;
        background: #161925;
        border: 1px solid #282E48;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.6);
        z-index: 99999;
        transition: opacity 0.12s ease-in-out;
        pointer-events: none;
    }
    .grid-node:hover .node-tooltip {
        visibility: visible;
        opacity: 1;
    }
    .tip-line {
        font-size: 11px;
        color: #E2E8F0;
        margin-bottom: 5px;
        white-space: nowrap;
        text-align: left;
    }
    .tip-line:last-child {
        margin-bottom: 0;
    }
    .tip-line span {
        font-weight: 700;
        color: #F4D068;
    }
</style>
<div class="casement-grid">
"""

# Render loop passing live data metrics directly to the interface layout
for wood_name in MEDALLION_COLUMNS:
    display_label = wood_name[:5].upper()
    owned = int(mock_user.get(wood_name, 0))
    
    # Map lowercase lookup key straight into database index
    lookup_key = wood_name.strip().lower()
    meta = live_metadata.get(lookup_key, {"Rarity": "Common", "Value": "$5", "Availability": "151", "Probability": "15.1%"})
    
    img_b64 = get_image_base64(f"assets/{wood_name.lower()}.png")
    
    # Append structured node segment
    html_elements += f"""
    <div class="grid-node">
        <div class="node-tooltip">
            <div class="tip-line">💎 Name: <span>{wood_name}</span></div>
            <div class="tip-line">🏷️ Rarity: <span>{meta['Rarity']}</span></div>
            <div class="tip-line">💰 Value: <span>{meta['Value']}</span></div>
            <div class="tip-line">📦 Avail: <span>{meta['Availability']} left</span></div>
            <div class="tip-line">🎲 Prob: <span>{meta['Probability']}</span></div>
        </div>
        
        <div class="image-frame">
            {"<img src='data:image/png;base64," + img_b64 + "' />" if (owned > 0 and img_b64) else "<div class='lock-node'>🔒</div>"}
        </div>
        
        <div class="quantity-badge">{"x" + str(owned) if owned > 0 else "&nbsp;"}</div>
        <div class="label-badge">{display_label}</div>
    </div>
    """

html_elements += "</div>"

# Render the single component with the optimal height boundary
st.components.v1.html(html_elements, height=280, scrolling=False)
