# ====================================================================
# PROJECT: TIMBER MEDALLION PORTFOLIO SYSTEM
# FILE: pages/store.py (ADAPTIVE ITEM PLATFORM)
# ====================================================================

import streamlit as st
import requests
import os
import base64

# Security Wall: Redirect if not authenticated via root login file
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("login.py")

st.set_page_config(page_title="Timber Reward Store", layout="wide", initial_sidebar_state="collapsed")

# 🎯 HORIZONTAL OPPOSITE-ALIGNMENT ENGINE
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
    }
    header, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; visibility: hidden; height: 0px; }
    
    div.block-container { padding-top: 20px !important; padding-bottom: 20px !important; }
    
    [data-testid="stVerticalBlock"] > div:has(div button[key="sys_back_dashboard_btn"]) {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }

    div[data-testid="element-container"]:has(button[key="sys_back_dashboard_btn"]) {
        display: inline-flex !important;
        width: auto !important;
    }

    /* ↩️ RETURN TO DASHBOARD BUTTON */
    div.stButton > button[key="sys_back_dashboard_btn"] {
        background-color: #161925 !important;
        border: 1px solid #23273A !important;
        color: #E2E8F0 !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        padding: 0.45rem 1.5rem !important;
        width: 240px !important;
        transition: all 0.2s ease !important;
        margin: 0 !important;
    }
    div.stButton > button[key="sys_back_dashboard_btn"]:hover {
        background-color: #23273A !important;
        border-color: #718096 !important;
        color: #FFF !important;
    }

    @media (max-width: 768px) {
        [data-testid="stVerticalBlock"] > div:has(div button[key="sys_back_dashboard_btn"]) {
            flex-direction: column !important;
            gap: 10px !important;
        }
        div.stButton > button[key="sys_back_dashboard_btn"] {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Navigation link back to main page
if st.button("Back to Portfolio ↩️", key="sys_back_dashboard_btn"):
    st.switch_page("pages/dashboard.py")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# ====================================================================
# REWARD STORE CONFIGURATION MATRIX (UPDATED ITEMS)
# ====================================================================
STORE_ITEMS = [
    {
        "id": "chocolate_bar",
        "title": "Premium Chocolate Bar",
        "cost": 150,
        "desc": "A rich, gourmet chocolate bar to sweeten your collection achievements.",
        "img_filename": "ChocolateBar.jpg"
    },
    {
        "id": "lollies",
        "title": "Mixed Candy Box",
        "cost": 250,
        "desc": "An assortment of premium lollies and sweet treats perfect for sharing.",
        "img_filename": "Lollies.jpg"
    },
    {
        "id": "pizza_voucher",
        "title": "Fresh Pizza Voucher",
        "cost": 600,
        "desc": "Redeemable for a hot, fresh pizza with your favorite toppings.",
        "img_filename": "Pizza.jpg"
    },
    {
        "id": "golden_nuggets",
        "title": "Crispy Chicken Nuggets",
        "cost": 800,
        "desc": "A golden, crispy share box of premium seasoned chicken nuggets.",
        "img_filename": "Nuggets.jpg"
    },
    {
        "id": "gift_cards",
        "title": "Digital Gift Card Bundle",
        "cost": 1500,
        "desc": "High-tier gift code token redeemable across major store networks.",
        "img_filename": "GiftCards.jpg"
    }
]

html_store_template = """
<style>
    body { margin: 0; padding: 0; background: transparent; font-family: 'Inter', sans-serif; color: #FFFFFF; }
    .store-header-wrapper { width: 100%; text-align: center; margin-bottom: 30px; box-sizing: border-box; padding: 0 10px; }
    
    .store-title { font-size: 26px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; letter-spacing: -0.5px; }
    .store-title span { color: #10B981; }
    .store-intro { max-width: 850px; margin: 0 auto; font-size: 13.5px; line-height: 1.6; color: rgba(255, 255, 255, 0.4); }

    .store-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; width: 100%; box-sizing: border-box; padding: 0 10px; margin-bottom: 40px; }
    .store-card { background: #161925; border: 1px solid #23273A; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; align-items: center; text-align: center; justify-content: space-between; transition: border-color 0.2s ease; }
    .store-card:hover { border-color: #10B981; }
    
    .item-image-frame { width: 100%; height: 160px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; background: #0E1117; border-radius: 6px; overflow: hidden; border: 1px solid #1E2235; }
    .item-image-frame img { max-width: 100%; max-height: 100%; object-fit: contain; }
    .item-fallback { font-size: 32px; }

    .item-title { font-size: 16px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px; }
    .item-desc { font-size: 12px; color: rgba(255, 255, 255, 0.4); line-height: 1.4; margin-bottom: 15px; min-height: 34px; }
    
    .item-cost-badge { font-size: 14px; font-weight: 700; color: #10B981; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 4px 12px; border-radius: 20px; margin-bottom: 15px; }
    
    .purchase-button { width: 100%; height: 38px; background-color: #10B981; border: none; border-radius: 6px; color: #FFFFFF; font-size: 12px; font-weight: 700; text-transform: uppercase; cursor: pointer; transition: background 0.2s ease; }
    .purchase-button:hover { background-color: #059669; }

    @media (max-width: 992px) {
        .store-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 600px) {
        .store-title { font-size: 22px; }
        .store-grid { grid-template-columns: repeat(1, 1fr); gap: 15px; }
        .item-image-frame { height: 180px; }
    }
</style>

<div class="store-header-wrapper">
    <div class="store-title">Timber Reward <span>Store</span></div>
    <div class="store-intro">
        Exchange your earned medallion points for real-world snacks and premium reward items. Select an available perk down below to submit a trade request voucher instantly.
    </div>
</div>

<div class="store-grid">__STORE_ITEMS_PLACEHOLDER__</div>

<script>
    function triggerRedemptionRequest(itemId, itemTitle, cost) {
        alert("Redemption order submitted for: " + itemTitle + "\\nCost: " + cost + " Points.\\nYour system balance will update shortly.");
    }
</script>
"""

grid_items_html = ""
for item in STORE_ITEMS:
    img_b64 = get_image_base64(f"assets/{item['img_filename']}")
    
    if img_b64:
        # Detect if it's a JPG/JPEG or PNG based on extension
        mime_type = "image/png" if item['img_filename'].lower().endswith('.png') else "image/jpeg"
        image_html = f"<img src='data:{mime_type};base64,{img_b64}' alt='{item['title']}' />"
    else:
        # Graceful fallback indicator if file isn't found locally yet
        image_html = "<div class='item-fallback'>🎁</div>"
        
    grid_items_html += f"""
    <div class="store-card">
        <div style="width: 100%;">
            <div class="item-image-frame">
                {image_html}
            </div>
            <div class="item-title">{item['title']}</div>
            <div class="item-desc">{item['desc']}</div>
        </div>
        <div style="width: 100%; display: flex; flex-direction: column; align-items: center;">
            <div class="item-cost-badge">{item['cost']} Points</div>
            <button class="purchase-button" onclick="triggerRedemptionRequest('{item['id']}', '{item['title']}', {item['cost']})">Claim Reward</button>
        </div>
    </div>
    """

html_store_elements = html_store_template.replace("__STORE_ITEMS_PLACEHOLDER__", grid_items_html)

st.components.v1.html(html_store_elements, height=900, scrolling=True)
