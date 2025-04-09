import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import requests
import sys
import os

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("whatsapp-analyzer-29d80-057eec373036.json")
    firebase_admin.initialize_app(cred)

# Firebase REST API key from your Firebase project settings
API_KEY = "AIzaSyBZHnloyhqWZt2tW4eVmp0rO7JwhDH-nQc"

# Firebase REST endpoint for login
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

# Sign Up Function (using Admin SDK)
def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user.uid
    except auth.AuthError as e:
        return str(e)
    except Exception as e:
        return str(e)

# Login Function (using REST API)
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
        if st.button("Sign Up"):
            if email and password:
                result = signup_user(email, password)
                if "Error" not in result:
                    st.success(f"User created successfully! Please login.")
                else:
                    st.error(f"Sign up failed: {result}")
            else:
                st.error("Please enter both email and password")
    
    elif auth_mode == "Login":
        if st.button("Login"):
            if email and password:
                result = login_user(email, password)
                if "idToken" in result:
                    st.session_state.user = result  # Save user info in session
                    st.session_state.authenticated = True
                    st.rerun()  # Rerun the app to show the main interface
                else:
                    st.error(f"Login failed: {result.get('error', 'Unknown error')}")
            else:
                st.error("Please enter both email and password")

def main():
    if not hasattr(st.session_state, 'authenticated'):
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        auth_page()
    else:
        # Import and run the main app
        from app import main as app_main
        app_main()

if __name__ == "__main__":
    main()