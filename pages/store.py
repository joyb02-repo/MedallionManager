# ====================================================================
# PROJECT: TIMBER MEDALLION PORTFOLIO SYSTEM
# FILE: pages/store.py (REWARDS BARTER & TRANSACTION ENGINE)
# ====================================================================

import streamlit as st
import requests
import os
import base64
import json

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

if st.button("Back to Portfolio ↩️", key="sys_back_dashboard_btn"):
    st.switch_page("pages/dashboard.py")

API_URL = st.secrets["API_URL"]
user_passcode = st.session_state.get("user_passcode", "DEFAULT_DEMO_KEY")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

@st.cache_data(ttl=5)
def fetch_sheet_records(passcode):
    try:
        r = requests.get(API_URL, params={"action": "fetchData", "passcode": passcode}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == "success":
                m_map = {str(m.get("Medallion", "")).strip().lower(): m for m in d.get("medallions", [])}
                summary = d.get("master_summary", {})
                return m_map, summary.get("Inventory", {}), summary.get("CollectionValue", "$0"), summary.get("MedallionsCollected", "0")
    except: pass
    return {}, {}, "$0", "0"

live_data, live_inventory, summary_value, summary_collected = fetch_sheet_records(user_passcode)

# Setup items array
STORE_ITEMS = [
    {"id": "chocolate_bar", "title": "Premium Chocolate Bar", "cost": 150, "desc": "A rich, gourmet chocolate bar to sweeten your achievements.", "img_filename": "ChocolateBar.jpg"},
    {"id": "lollies", "title": "Mixed Candy Box", "cost": 250, "desc": "An assortment of premium lollies and sweet treats perfect for sharing.", "img_filename": "Lollies.jpg"},
    {"id": "pizza_voucher", "title": "Fresh Pizza Voucher", "cost": 600, "desc": "Redeemable for a hot, fresh pizza with your favorite toppings.", "img_filename": "Pizza.jpg"},
    {"id": "golden_nuggets", "title": "Crispy Chicken Nuggets", "cost": 800, "desc": "A golden, crispy share box of premium seasoned chicken nuggets.", "img_filename": "Nuggets.jpg"},
    {"id": "gift_cards", "title": "Digital Gift Card Bundle", "cost": 1500, "desc": "High-tier gift code token redeemable across major store networks.", "img_filename": "GiftCards.jpg"}
]

# Serialized conversion profiles for JavaScript processing
items_json = json.dumps(STORE_ITEMS)
inventory_json = json.dumps({k: int(v) for k, v in live_inventory.items() if int(v) > 0})

medallion_details = {}
for k, v in live_data.items():
    raw_val = str(v.get("Value", "0")).replace("$", "").replace(",", "").strip()
    try: val_int = int(float(raw_val))
    except: val_int = 0
    medallion_details[k] = {"name": v.get("Medallion", k.capitalize()), "value": val_int}
medallions_json = json.dumps(medallion_details)

html_store_template = """
<style>
    body { margin: 0; padding: 0; background: transparent; font-family: 'Inter', sans-serif; color: #FFFFFF; }
    .store-header-wrapper { width: 100%; text-align: center; margin-bottom: 25px; box-sizing: border-box; padding: 0 10px; }
    .store-title { font-size: 26px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; letter-spacing: -0.5px; }
    .store-title span { color: #10B981; }
    .store-intro { max-width: 850px; margin: 0 auto; font-size: 13.5px; line-height: 1.6; color: rgba(255, 255, 255, 0.4); }

    .dashboard-row { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; padding: 0 10px; }
    .stat-card { background: #161925; border: 1px solid #23273A; border-radius: 6px; padding: 12px 24px; min-width: 190px; text-align: center; flex: 1; max-width: 240px; }
    .stat-label { font-size: 11px; text-transform: uppercase; color: #718096; margin-bottom: 4px; letter-spacing: 0.5px; }
    .stat-value { font-size: 20px; font-weight: 700; color: #F4D068; }

    .store-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; width: 100%; box-sizing: border-box; padding: 0 10px; margin-bottom: 35px; }
    .store-card { background: #161925; border: 1px solid #23273A; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; align-items: center; text-align: center; justify-content: space-between; }
    
    .item-image-frame { width: 100%; height: 140px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; background: #0E1117; border-radius: 6px; overflow: hidden; border: 1px solid #1E2235; }
    .item-image-frame img { max-width: 100%; max-height: 100%; object-fit: contain; }
    
    .item-title { font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px; }
    .item-desc { font-size: 12px; color: rgba(255, 255, 255, 0.4); line-height: 1.4; margin-bottom: 15px; min-height: 34px; }
    .item-cost-badge { font-size: 13px; font-weight: 700; color: #10B981; margin-bottom: 15px; }
    
    /* QUANTITY MANAGER CONTROLS */
    .qty-container { display: flex; align-items: center; gap: 12px; background: #0E1117; border: 1px solid #23273A; border-radius: 6px; padding: 4px 10px; margin-bottom: 5px; }
    .qty-btn { background: transparent; border: none; color: #718096; font-size: 16px; font-weight: bold; cursor: pointer; padding: 0 6px; user-select: none; }
    .qty-btn:hover { color: #FFF; }
    .qty-display { font-size: 14px; font-weight: 700; color: #FFF; min-width: 20px; text-align: center; }

    .checkout-bar-container { display: flex; justify-content: center; margin-bottom: 40px; }
    .checkout-trigger-btn { width: 424px; max-width: 100%; height: 48px; background: linear-gradient(135deg, #10B981 0%, #059669 100%); border: none; border-radius: 6px; color: #FFF; font-size: 14px; font-weight: 700; text-transform: uppercase; cursor: pointer; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2); }
    .checkout-trigger-btn:disabled { opacity: 0.35; cursor: not-allowed; background: #161925; box-shadow: none; border: 1px solid #23273A; }

    /* CHECKOUT MODAL OVERLAY SHEET */
    .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(14, 17, 23, 0.9); backdrop-filter: blur(4px); display: none; align-items: flex-start; justify-content: center; z-index: 99999; padding-top: 40px; overflow-y: auto; box-sizing: border-box; }
    .modal-box { background: #0E1117; border: 1px solid #23273A; border-radius: 12px; width: 480px; max-width: 95%; padding: 25px; box-shadow: 0 20px 40px rgba(0,0,0,0.7); box-sizing: border-box; margin-bottom: 40px; }
    .modal-title { font-size: 20px; font-weight: 700; color: #FFF; margin-bottom: 15px; }
    
    .summary-section { background: #161925; border: 1px solid #23273A; border-radius: 6px; padding: 12px; margin-bottom: 20px; text-align: left; }
    .summary-row { display: flex; justify-content: space-between; font-size: 13px; color: rgba(255,255,255,0.6); margin-bottom: 6px; }
    .summary-row.total-line { border-top: 1px solid #23273A; padding-top: 8px; margin-top: 8px; font-weight: 700; color: #10B981; font-size: 15px; }

    .inventory-barter-list { max-height: 200px; overflow-y: auto; text-align: left; margin-bottom: 20px; background: #0E1117; border: 1px solid #23273A; border-radius: 6px; padding: 8px; }
    .barter-item-row { display: flex; align-items: center; justify-content: space-between; padding: 8px; border-bottom: 1px solid #161925; }
    .barter-label-group { display: flex; flex-direction: column; }
    .barter-title { font-size: 13px; font-weight: 600; color: #FFF; }
    .barter-meta { font-size: 11px; color: #718096; }

    .barter-selector-wrap { display: flex; align-items: center; gap: 8px; }
    .barter-select { background: #161925; border: 1px solid #23273A; color: #FFF; border-radius: 4px; padding: 4px; font-size: 12px; outline: none; }

    .error-log-banner { color: #EF4444; font-size: 12px; font-weight: 600; min-height: 18px; margin-bottom: 15px; text-align: center; }
    .finalize-btn { width: 100%; height: 42px; background: #F4D068; color: #0E1117; border: none; border-radius: 6px; font-size: 13px; font-weight: 700; text-transform: uppercase; cursor: pointer; }
    .finalize-btn:disabled { background: #161925 !important; color: #3D4563 !important; border: 1px solid #23273A; cursor: not-allowed; }
    .close-modal-link { color: #718096; font-size: 12px; margin-top: 14px; display: inline-block; cursor: pointer; text-decoration: underline; }

    @media (max-width: 992px) { .store-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 600px) {
        .store-title { font-size: 22px; }
        .store-grid { grid-template-columns: repeat(1, 1fr); gap: 15px; }
        .dashboard-row { gap: 10px; }
        .stat-card { padding: 10px; min-width: 0; }
        .stat-value { font-size: 16px; }
    }
</style>

<div class="store-header-wrapper">
    <div class="store-title">Timber Reward <span>Store</span></div>
    <div class="store-intro">Exchange your earned portfolio asset evaluations for real-world snacks and prize categories. Use your layout indicators to manage multiple quantities before initializing checkouts.</div>
</div>

<div class="dashboard-row">
    <div class="stat-card"><div class="stat-label">Portfolio Evaluation</div><div class="stat-value">__VALUE_PLACEHOLDER__</div></div>
    <div class="stat-card"><div class="stat-label">Total Medallions</div><div class="stat-value">__COLLECTED_PLACEHOLDER__</div></div>
</div>

<div class="store-grid">__STORE_ITEMS_PLACEHOLDER__</div>

<div class="checkout-bar-container">
    <button class="checkout-trigger-btn" id="basketCheckoutBtn" disabled onclick="openCheckoutBale()">Proceed to Verification Checkout</button>
</div>

<div class="modal-overlay" id="checkoutModal">
    <div class="modal-box">
        <div class="modal-title">Verify Trade Voucher</div>
        
        <div class="summary-section" id="cartSummaryContainer"></div>
        
        <div style="text-align:left; font-size:12px; font-weight:700; color:#718096; text-transform:uppercase; margin-bottom:8px; letter-spacing:0.5px;">Select Barter Coverage:</div>
        <div class="inventory-barter-list" id="barterListDom"></div>
        
        <div class="summary-section">
            <div class="summary-row"><span>Total Cart Cost:</span><span id="labelSummaryCost">0 pts</span></div>
            <div class="summary-row"><span>Selected Barter Value:</span><span id="labelSummaryBarter" style="color:#F4D068;">$0</span></div>
        </div>

        <div class="error-log-banner" id="checkoutErrLog"></div>
        <button class="finalize-btn" id="finalTradeBtn" disabled onclick="executeFinalTransaction()">Finalise Trade Voucher</button>
        <div class="close-modal-link" onclick="closeCheckoutBale()">Cancel & Modify Basket</div>
    </div>
</div>

<script>
    const itemCatalog = __CATALOG_JSON__;
    const userInventory = __INVENTORY_JSON__;
    const medallionMetadata = __MEDALLIONS_JSON__;
    const endpoint = "__API_URL_PLACEHOLDER__";
    
    let cart = {};

    function updateItemQuantity(itemId, adjustment) {
        if (!cart[itemId]) cart[itemId] = 0;
        cart[itemId] = Math.max(0, cart[itemId] + adjustment);
        document.getElementById("qty_val_" + itemId).innerText = cart[itemId];
        evaluateBasketStatus();
    }

    function evaluateBasketStatus() {
        let totalCount = 0;
        for (let key in cart) { totalCount += cart[key]; }
        document.getElementById("basketCheckoutBtn").disabled = (totalCount === 0);
    }

    function openCheckoutBale() {
        buildCartSummary();
        buildBarterInventoryList();
        recalculateBarterMath();
        document.getElementById("checkoutModal").style.display = "flex";
    }

    function closeCheckoutBale() {
        document.getElementById("checkoutModal").style.display = "none";
    }

    function buildCartSummary() {
        const container = document.getElementById("cartSummaryContainer");
        container.innerHTML = "";
        let totalPrice = 0;
        for (let itemId in cart) {
            if (cart[itemId] > 0) {
                const item = itemCatalog.find(i => i.id === itemId);
                const lineCost = item.cost * cart[itemId];
                totalPrice += lineCost;
                container.innerHTML += `<div class="summary-row"><span>${item.title} (x${cart[itemId]})</span><span>${lineCost} pts</span></div>`;
            }
        }
        container.innerHTML += `<div class="summary-row total-line"><span>Total Balance Due:</span><span>${totalPrice} Points</span></div>`;
        document.getElementById("labelSummaryCost").innerText = totalPrice + " pts";
    }

    function buildBarterInventoryList() {
        const target = document.getElementById("barterListDom");
        target.innerHTML = "";
        let inventoryEmpty = true;

        for (let key in userInventory) {
            const ownedQty = userInventory[key];
            if (ownedQty > 0) {
                inventoryEmpty = false;
                const meta = medallionMetadata[key] || {name: key.toUpperCase(), value: 0};
                let optionsHtml = "";
                for (let i = 0; i <= ownedQty; i++) {
                    optionsHtml += `<option value="${i}">${i}</option>`;
                }
                target.innerHTML += `
                    <div class="barter-item-row">
                        <div class="barter-label-group">
                            <span class="barter-title">${meta.name}</span>
                            <span class="barter-meta">Value: $${meta.value} | Available: x${ownedQty}</span>
                        </div>
                        <div class="barter-selector-wrap">
                            <select class="barter-select" data-key="${key}" data-value="${meta.value}" onchange="recalculateBarterMath()">
                                ${optionsHtml}
                            </select>
                        </div>
                    </div>
                `;
            }
        }
        if (inventoryEmpty) {
            target.innerHTML = `<div style="text-align:center; padding:20px; font-size:12px; color:#718096;">No collected medallions found in active portfolio database.</div>`;
        }
    }

    function recalculateBarterMath() {
        let totalCost = 0;
        for (let itemId in cart) {
            if (cart[itemId] > 0) {
                const item = itemCatalog.find(i => i.id === itemId);
                totalCost += (item.cost * cart[itemId]);
            }
        }

        let totalBarterProvided = 0;
        const selects = document.querySelectorAll(".barter-select");
        selects.forEach(sel => {
            const qtySelected = parseInt(sel.value) || 0;
            const singleValue = parseInt(sel.getAttribute("data-value")) || 0;
            totalBarterProvided += (qtySelected * singleValue);
        });

        document.getElementById("labelSummaryBarter").innerText = "$" + totalBarterProvided;
        const errorLog = document.getElementById("checkoutErrLog");
        const tradeBtn = document.getElementById("finalTradeBtn");

        if (totalBarterProvided >= totalCost) {
            errorLog.innerText = "";
            tradeBtn.disabled = false;
        } else {
            errorLog.innerText = "Insufficient barter value. Covered value must equal or exceed point cost.";
            tradeBtn.disabled = true;
        }
    }

    function executeFinalTransaction() {
        const tradeBtn = document.getElementById("finalTradeBtn");
        tradeBtn.disabled = true;
        tradeBtn.innerText = "Processing Trade Voucher...";

        const selects = document.querySelectorAll(".barter-select");
        let itemsSpentMap = {};
        selects.forEach(sel => {
            const q = parseInt(sel.value) || 0;
            if (q > 0) {
                itemsSpentMap[sel.getAttribute("data-key")] = q;
            }
        });

        let finalBasketItems = {};
        for (let key in cart) {
            if (cart[key] > 0) finalBasketItems[key] = cart[key];
        }

        const payload = {
            passcode: "__PASSCODE_RAW__",
            basket: finalBasketItems,
            barter_spent: itemsSpentMap
        };

        const targetUrl = endpoint + "?action=executeStoreTrade&payload=" + encodeURIComponent(json.dumps(payload));
        const transactionPing = new Image();
        transactionPing.onload = transactionPing.onerror = function() {
            setTimeout(() => {
                const parentDoc = window.parent.document;
                const refreshActuator = Array.from(parentDoc.querySelectorAll('button')).find(el => el.innerText.includes('Update Data 🔄'));
                if (refreshActuator) refreshActuator.click();
                else window.location.reload();
            }, 500);
        };
        transactionPing.src = targetUrl;
    }
</script>
"""

grid_items_html = ""
for item in STORE_ITEMS:
    img_b64 = get_image_base64(f"assets/{item['img_filename']}")
    mime_type = "image/png" if item['img_filename'].lower().endswith('.png') else "image/jpeg"
    image_html = f"<img src='data:{mime_type};base64,{img_b64}' alt='{item['title']}' />" if img_b64 else "<div class='item-fallback'>🎁</div>"
        
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
            <div class="qty-container">
                <button class="qty-btn" onclick="updateItemQuantity('{item['id']}', -1)">-</button>
                <div class="qty-display" id="qty_val_{item['id']}">0</div>
                <button class="qty-btn" onclick="updateItemQuantity('{item['id']}', 1)">+</button>
            </div>
        </div>
    </div>
    """

# Variable Injection Pipeline
html_store_elements = html_store_template.replace("__STORE_ITEMS_PLACEHOLDER__", grid_items_html)
html_store_elements = html_store_elements.replace("__VALUE_PLACEHOLDER__", summary_value)
html_store_elements = html_store_elements.replace("__COLLECTED_PLACEHOLDER__", summary_collected)
html_store_elements = html_store_elements.replace("__CATALOG_JSON__", items_json)
html_store_elements = html_store_elements.replace("__INVENTORY_JSON__", inventory_json)
html_store_elements = html_store_elements.replace("__MEDALLIONS_JSON__", medallions_json)
html_store_elements = html_store_elements.replace("__PASSCODE_RAW__", user_passcode)
html_store_elements = html_store_elements.replace("__API_URL_PLACEHOLDER__", API_URL)

st.components.v1.html(html_store_elements, height=950, scrolling=True)
