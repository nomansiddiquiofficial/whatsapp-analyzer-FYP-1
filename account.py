import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("whatsapp-analyzer-29d80-057eec373036.json")
    firebase_admin.initialize_app(cred)

# REST API key
API_KEY = "AIzaSyBZHnloyhqWZt2tW4eVmp0rO7JwhDH-nQc"
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user.uid
    except Exception as e:
        return str(e)

def login_user(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        res = requests.post(FIREBASE_SIGNIN_URL, json=payload)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def auth_page():
    st.title("📱 WhatsApp Analyzer Login / Sign Up")
    auth_mode = st.radio("Choose mode", ["Login", "Sign Up"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if auth_mode == "Sign Up":
        if st.button("Sign Up") and email and password:
            result = signup_user(email, password)
            if "Error" not in result:
                st.success(f"User created successfully! Please login.")
            else:
                st.error(f"Sign up failed: {result}")
    elif auth_mode == "Login":
        if st.button("Login") and email and password:
            result = login_user(email, password)
            if "idToken" in result:
                st.session_state.user = result
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error(f"Login failed: {result.get('error', 'Unknown error')}")

def main():
    if not hasattr(st.session_state, 'authenticated'):
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        auth_page()
    else:
        from app import main as app_main
        app_main()

if __name__ == "__main__":
    main()
