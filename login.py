# ====================================================================
# PROJECT: TIMBER MEDALLION PORTFOLIO SYSTEM
# FILE: login.py (GATEWAY CONFIGURATION)
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

# Global UI Inject Style Framework for Gateway Box
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
    }
    header, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; visibility: hidden; height: 0px; }
    
    /* Login Form Frame Styling */
    div[data-testid="stForm"] {
        background: #161925 !important;
        border: 1px solid #23273A !important;
        border-radius: 12px !important;
        padding: 40px 40px !important;
        max-width: 440px !important;
        margin: 120px auto 0 auto !important;
        box-shadow: 0 20px 45px rgba(0,0,0,0.5) !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    .login-logo-container { width: 100%; text-align: center; margin-bottom: 20px; }
    .login-logo-container img { max-height: 60px; width: auto; object-fit: contain; }
    .custom-login-header { font-size: 22px; font-weight: 600; color: #FFFFFF; margin-bottom: 10px; letter-spacing: 0.5px; font-family: 'Inter', sans-serif; }
    .custom-login-sub { font-size: 13px; color: rgba(255, 255, 255, 0.4); margin-bottom: 30px; line-height: 1.5; font-family: 'Inter', sans-serif; }
    
    /* Masked pass dots code entry input layout styling */
    div[data-testid="stForm"] div[data-testid="stTextInput"] { max-width: 220px !important; margin: 0 auto 24px auto !important; }
    div[data-testid="stForm"] input {
        background-color: #0E1117 !important; border: 1px solid #23273A !important; border-radius: 6px !important;
        color: #FFF !important; text-align: center !important; font-size: 36px !important; font-weight: 700 !important;
        letter-spacing: 12px !important; height: 52px !important; box-sizing: border-box !important; padding: 0px 0px 0px 12px !important;
        -webkit-text-security: disc !important;
    }
    div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
        width: 100% !important; height: 46px !important; background-color: #F4D068 !important; border: none !important; border-radius: 6px !important;
        color: #0E1117 !important; font-size: 13px !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1.5px !important;
    }
</style>
""", unsafe_allow_html=True)

with st.form("secure_login_gateway"):
    if logo_b64:
        st.markdown(f'<div class="login-logo-container"><img src="data:image/png;base64,{logo_b64}" /></div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-login-header">Portfolio System Access</div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-login-sub">Enter your 4-digit master passcode key to authenticate transaction nodes.</div>', unsafe_allow_html=True)
    
    input_passcode = st.text_input("Passcode", type="password", label_visibility="collapsed", max_chars=4)
    submit_btn = st.form_submit_button("Verify Passcode")
    
    if submit_btn:
        if len(input_passcode) < 4:
            st.error("Please complete passcode entry.")
        else:
            with st.spinner("AUTHENTICATING..."):
                try:
                    chk = requests.get(API_URL, params={"action": "fetchData", "passcode": input_passcode}, timeout=12)
                    if chk.status_code == 200 and chk.json().get("status") == "success":
                        st.session_state["user_passcode"] = input_passcode
                        st.session_state["username"] = chk.json().get("username", "User")
                        st.session_state["authenticated"] = True
                        st.switch_page("pages/dashboard.py")
                    else:
                        st.error("Access Denied: Passcode signature validation rejected.")
                except:
                    st.error("System Matrix Timeout. Please check your network connection.")
