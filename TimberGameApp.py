import streamlit as st
import random

# --- INITIALIZE APP STATE ---
if 'balance' not in st.session_state:
    st.session_state.balance = 250  # Starting cash
if 'spending' not in st.session_state:
    st.session_state.spending = 0
if 'completed_count' not in st.session_state:
    st.session_state.completed_count = 0
if 'logs' not in st.session_state:
    st.session_state.logs = [" Clocked in. Welcome to the workshop floor, Apprentice!"]

# Initialize 10 empty slot spaces for showcase items
if 'slots' not in st.session_state:
    st.session_state.slots = {f"Slot {i+1}": "Empty" for i in range(10)}

# Dynamic pool of interactive jobs
JOB_POOL = [
    {"name": "🛹 Custom Skateboard", "cost": 40, "payout": 110, "risk": "Medium"},
    {"name": "🎸 Mahogany Ukulele", "cost": 80, "payout": 220, "risk": "High"},
    {"name": "📥 Pine Desk Organizer", "cost": 20, "payout": 55, "risk": "Low"},
    {"name": "🪑 Red Oak Milking Stool", "cost": 50, "payout": 135, "risk": "Medium"},
    {"name": "🐦 Eco-Friendly Birdhouse", "cost": 15, "payout": 40, "risk": "Low"},
    {"name": "⚔️ Ornamental Wooden Sword", "cost": 30, "payout": 85, "risk": "High"}
]

# Generate 3 active unique random job offers on first load or refresh
if 'active_jobs' not in st.session_state:
    st.session_state.active_jobs = random.sample(JOB_POOL, 3)

# --- PAGE SETUP & SLEEK THEME ---
st.set_page_config(page_title="Apprentice Dashboard", page_icon="🪵", layout="wide")

st.markdown("""
    <style>
    /* Sleek Dark Cyber-Wood Theme Layout */
    .reportview-container { background: #0e1117; }
    .main-header { font-family: 'Helvetica Neue', sans-serif; font-weight: 800; font-size: 2.5rem; color: #f4d068; letter-spacing: -1px; }
    .metric-card { background: #1a1c24; border: 1px solid #2d313f; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    .metric-val { font-size: 1.8rem; font-weight: bold; color: #ffffff; margin-top: 5px; }
    .metric-lbl { font-size: 0.9rem; color: #8a92a6; text-transform: uppercase; letter-spacing: 1px; }
    .slot-card-empty { background: #16171d; border: 2px dashed #3a3f50; padding: 25px; border-radius: 10px; text-align: center; color: #58617a; font-weight: 500; font-size: 1rem; }
    .slot-card-filled { background: linear-gradient(135deg, #2b2318, #1a140e); border: 2px solid #f4d068; padding: 25px; border-radius: 10px; text-align: center; color: #f4d068; font-weight: bold; box-shadow: 0 4px 15px rgba(244,208,104,0.1); }
    .log-box { background-color: #0b0c10; color: #a4b3c6; padding: 15px; border-radius: 8px; font-family: monospace; height: 120px; overflow-y: auto; border: 1px solid #22252e; font-size: 0.85rem; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ROW ---
st.markdown("<div class='main-header'>🪵 Apprentice Workshop Floor</div>", unsafe_allow_html=True)
st.write("Manage contracts, source supplies, and craft your way up to fill your showcase showroom.")
st.write("---")

# --- LIVE METRIC DASHBOARD ROW ---
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.markdown(f"<div class='metric-card'><div class='metric-lbl'>💳 Bank Balance</div><div class='metric-val' style='color: #00ffcc;'>${st.session_state.balance}</div></div>", unsafe_allow_html=True)
with m_col2:
    st.markdown(f"<div class='metric-card'><div class='metric-lbl'>📈 Total Spendings</div><div class='metric-val' style='color: #ff4d4d;'>${st.session_state.spending}</div></div>", unsafe_allow_html=True)
with m_col3:
    st.markdown(f"<div class='metric-card'><div class='metric-lbl'>💼 Active Offers</div><div class='metric-val' style='color: #f4d068;'>{len(st.session_state.active_jobs)} Available</div></div>", unsafe_allow_html=True)
with m_col4:
    st.markdown(f"<div class='metric-card'><div class='metric-lbl'>🛠️ Completed Jobs</div><div class='metric-val' style='color: #b388ff;'>{st.session_state.completed_count} Done</div></div>", unsafe_allow_html=True)

st.write("")

# --- MAIN WORKSPACE INTERACTION ---
left_panel, right_panel = st.columns([3, 2])

with left_panel:
    st.subheader("📋 Available Job Board")
    st.write("Review material startup costs and execute client commissions:")
    
    # Render Job Cards dynamically
    for index, job in enumerate(st.session_state.active_jobs):
        with st.container():
            col_j1, col_j2, col_j3 = st.columns([2, 1, 1])
            with col_j1:
                st.markdown(f"**{job['name']}**")
                st.caption(f"Risk Profile: `{job['risk']}` Risk Matrix")
            with col_j2:
                st.markdown(f"<span style='color: #ff4d4d;'>Cost: -${job['cost']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color: #00ffcc;'>Pay: +${job['payout']}</span>", unsafe_allow_html=True)
            with col_j3:
                # Disable if player can't afford upfront costs
                can_afford = st.session_state.balance >= job['cost']
                if st.button(f"Accept Contract", key=f"job_{index}", disabled=not can_afford):
                    # Handle financial flow
                    st.session_state.balance -= job['cost']
                    st.session_state.spending += job['cost']
                    
                    # Core Luck Roll Mechanics
                    risk_roll = random.randint(1, 100)
                    failure_threshold = 10 if job['risk'] == "Low" else (30 if job['risk'] == "Medium" else 50)
                    
                    if risk_roll > failure_threshold:
                        # SUCCESS! Payout and map to slot grid
                        st.session_state.balance += job['payout']
                        st.session_state.completed_count += 1
                        
                        # Find the first vacant layout slot card to plug item into
                        assigned_slot = None
                        for s_key, s_val in st.session_state.slots.items():
                            if s_val == "Empty":
                                st.session_state.slots[s_key] = job['name']
                                assigned_slot = s_key
                                break
                        
                        slot_log = f" placed in {assigned_slot}!" if assigned_slot else " (No free showroom spaces left!)"
                        st.session_state.logs.append(f"✅ Crafted '{job['name']}' successfully! Netting profit.{slot_log}")
                    else:
                        # FAILURE / KNOT / SPLINTER DEFECTS
                        st.session_state.logs.append(f"❌ Structural Failure! Slipped on assembly blueprint for '{job['name']}'. Scrap discarded.")
                    
                    # Cycle board offers instantly
                    st.session_state.active_jobs = random.sample(JOB_POOL, 3)
                    st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: #22252e;'>", unsafe_allow_html=True)

with right_panel:
    st.subheader("📟 Workbench Feed Logs")
    # Clean terminal stream logger container
    logs_reversed = "<br>".join([f"🛠️ {log}" for log in reversed(st.session_state.logs)])
    st.markdown(f"<div class='log-box'>{logs_reversed}</div>", unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 Liquidate / Wipe All Storage Boards", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.write("---")

# --- THE 10 DISPLAY CARD SLOTS GRID ---
st.subheader("📦 Workshop Showcase Inventory (10 Slots Total)")
st.write("Keep your output steady to plug item positions and clean out the blank canvas bays:")

# Map out layout positions into responsive grid splits
slots_keys = list(st.session_state.slots.keys())
row1_slots = slots_keys[:5]
row2_slots = slots_keys[5:]

# Render First 5 Slots
row1_cols = st.columns(5)
for idx, slot_id in enumerate(row1_slots):
    item = st.session_state.slots[slot_id]
    with row1_cols[idx]:
        if item == "Empty":
            st.markdown(f"<div class='slot-card-empty'>{slot_id}<br><span style='font-size:0.75rem; color:#434b5e;'>VACANT</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='slot-card-filled'>{slot_id}<br><span style='font-size:0.85rem;'>{item}</span></div>", unsafe_allow_html=True)

st.write("") # Margin Padding

# Render Second 5 Slots
row2_cols = st.columns(5)
for idx, slot_id in enumerate(row2_slots):
    item = st.session_state.slots[slot_id]
    with row2_cols[idx]:
        if item == "Empty":
            st.markdown(f"<div class='slot-card-empty'>{slot_id}<br><span style='font-size:0.75rem; color:#434b5e;'>VACANT</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='slot-card-filled'>{slot_id}<br><span style='font-size:0.85rem;'>{item}</span></div>", unsafe_allow_html=True)
