# ====================================================================
# PROJECT: TIMBER MEDALLION PORTFOLIO SYSTEM
# FILE: login.py (SCALE-TO-FIT FIXED DESIGN)
# ====================================================================

import streamlit as st
import requests
import os
import base64

API_URL = st.secrets["API_URL"]

st.set_page_config(page_title="Timber Medallion Portfolio", layout="wide", initial_sidebar_state="collapsed")

# Initialize session structures safely
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_passcode" not in st.session_state:
    st.session_state["user_passcode"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = "Guest"

# Route immediately if already authenticated
if st.session_state["authenticated"]:
    st.switch_page("pages/dashboard.py")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

logo_b64 = get_image_base64("assets/login_logo.png")

# Persistent connection pooling to eliminate false timeouts
@st.cache_resource(ttl=600)
def get_http_session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

# Global UI Style Framework - Scale calculations tied strictly to screen viewport constraints
st.markdown("""
<style>
    /* Absolute containment framework to break Streamlit's scrolling mechanics */
    html, body, .stApp, [data-testid="stMain"], [data-testid="stMainContainer"], .main, .block-container {
        margin: 0 !important;
        padding: 0 !important;
        height: 100dvh !important;
        min-height: 100dvh !important;
        max-height: 100dvh !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        box-sizing: border-box !important;
    }

    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
    }
    
    header, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; visibility: hidden; height: 0px; }
    
    /* REMOVE THE MASSIVE OUTER DIALOGUE BACKGROUND CONTAINER */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* The Central Core Login Card Frame - Uses dynamic layout calculations to automatically scale with viewport heights */
    div[data-testid="stVerticalBlock"]:has(div.login-card-anchor) {
        background: #161925 !important;
        border: 1px solid #23273A !important;
        border-radius: 12px !important;
        padding: min(5vh, 40px) min(5vw, 45px) !important;
        max-width: 440px !important;
        width: min(440px, 90vw) !important;
        max-height: 85vh !important; /* Prevents container from ever bleeding past screen edge heights */
        margin: auto !important; 
        box-shadow: 0 20px 45px rgba(0,0,0,0.5) !important;
        text-align: center !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Fluid Logo Component scaling bounds */
    .login-logo-container { width: 100%; text-align: center; margin-bottom: min(3vh, 25px); display: flex; justify-content: center; }
    .login-logo-container img { height: min(15vh, 130px); width: auto; object-fit: contain; }
    
    .custom-login-header { font-size: min(5vw, 22px); font-weight: 600; color: #FFFFFF; margin-bottom: min(1.5vh, 10px); width: 100%; text-align: center !important; letter-spacing: 0.5px; font-family: 'Inter', sans-serif; }
    .custom-login-sub { font-size: min(3.5vw, 13px); color: rgba(255, 255, 255, 0.4); margin-bottom: min(4vh, 30px); width: 100%; text-align: center !important; line-height: 1.5; font-family: 'Inter', sans-serif; }
    
    /* Passcode Wrapper Frame Input Column constraints */
    div.stTextInput { width: min(160px, 45vw) !important; margin: 0 auto min(1vh, 5px) auto !important; }
    
    div[data-testid="stTextInput"] div[data-component="stTextInputRootElement"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: min(6vh, 46px) !important;
        box-sizing: border-box !important;
    }
    
    div.stTextInput input {
        background-color: #0E1117 !important; border: 1px solid #23273A !important; border-radius: 6px !important;
        color: #FFF !important; text-align: center !important; font-size: min(5.5vw, 24px) !important; font-weight: 700 !important;
        letter-spacing: 6px !important; height: 100% !important; box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        line-height: normal !important;
    }
    
    div[data-testid="stTextInput"] button {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
        margin-top: 0px !important;
        margin-bottom: 0px !important;
    }
    
    div.stTextInput p, [data-testid="stWidgetInstructions"] { 
        display: none !important; 
        visibility: hidden !important; 
        height: 0px !important; 
        margin: 0px !important; 
        padding: 0px !important; 
    }
    
    /* Submission Interface triggers */
    div.stButton {
        width: 100% !important;
        margin: min(3vh, 25px) 0 0 0 !important;
        padding: 0 !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    div.stButton > button {
        width: 100% !important; 
        height: min(7vh, 50px) !important; 
        background-color: #F4D068 !important; 
        border: none !important; 
        border-radius: 8px !important;
        color: #0E1117 !important; 
        font-size: min(4vw, 14px) !important; 
        font-weight: 700 !important; 
        text-transform: uppercase !important; 
        letter-spacing: 1.5px !important;
        text-align: center !important;
        margin: 0 !important;
        display: block !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(244, 208, 104, 0.1) !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div.stButton > button:hover {
        background-color: #f5d77f !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(244, 208, 104, 0.25) !important;
    }
    
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    div[data-testid="stAlert"] { margin-top: min(1.5vh, 15px) !important; width: 100% !important; }

    /* For extremely short display heights (like landscape phones), scale back proportions */
    @media (max-height: 580px) {
        div[data-testid="stVerticalBlock"]:has(div.login-card-anchor) {
            padding: 15px 30px !important;
        }
        .login-logo-container { margin-bottom: 5px !important; }
        .custom-login-sub { margin-bottom: 12px !important; }
        div.stButton { margin-top: 10px !important; }
    }
</style>
""", unsafe_allow_html=True)

# Build anchor flag mapping target
st.markdown('<div class="login-card-anchor"></div>', unsafe_allow_html=True)

if logo_b64:
    st.markdown(f'<div class="login-logo-container"><img src="data:image/png;base64,{logo_b64}" /></div>', unsafe_allow_html=True)

st.markdown('<div class="custom-login-header">Medallion Management Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-login-sub">Enter your 4-digit master passcode key to access your Medallion Management Portal dashboard.</div>', unsafe_allow_html=True)

input_passcode = st.text_input("Passcode", type="password", label_visibility="collapsed", max_chars=4)
submit_btn = st.button("Verify Passcode")

if submit_btn:
    if len(input_passcode) < 4:
        st.error("Please complete passcode entry.")
    else:
        with st.spinner("AUTHENTICATING..."):
            try:
                http_client = get_http_session()
                chk = http_client.get(API_URL, params={"action": "fetchData", "passcode": input_passcode}, timeout=15)
                
                if chk.status_code == 200 and chk.json().get("status") == "success":
                    st.session_state["user_passcode"] = input_passcode
                    st.session_state["username"] = chk.json().get("username", "User")
                    st.session_state["authenticated"] = True
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("Access Denied: Passcode signature validation rejected.")
            except Exception as e:
                st.error("System Matrix Timeout. Please check your network connection.")
