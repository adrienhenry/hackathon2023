import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import streamlit as st
import time
import pickle as pkl
import pandas as pd

authenticator = None


def load_credentials(credential_file):
    credentials = pkl.load(open(credential_file, "rb"))
    return credentials


def handle_login(credential_file):
    global authenticator
    credentials = load_credentials(credential_file)
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name="hackathon_authenticator",
        key="hackathon_authenticator",
        cookie_expiry_days=1,
    )
    name, authentication_status, username = authenticator.login("Login", "main")


def handle_authentication_status():
    if st.session_state["authentication_status"]:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"You are logged in as {st.session_state['name']}")
        with col2:
            authenticator.logout("Logout", "main")
        return True
    if st.session_state["authentication_status"] == False:
        st.error("Username/password is incorrect")
    if st.session_state["authentication_status"] == None:
        st.warning("Please enter your username and password")
    return False


#     global authenticator
#     with open(credential_file) as file:
#         config = yaml.load(file, Loader=SafeLoader)
#     authenticator = stauth.Authenticate(
#         config["credentials"],
#         config["cookie"]["name"],
#         config["cookie"]["key"],
#         config["cookie"]["expiry_days"],
#         config["preauthorized"],
#     )
#     name, authentication_status, username = authenticator.login("Login", "main")
#     if authentication_status:
#         return
#     elif authentication_status is False:
#         st.error("Username/password is incorrect")
#     elif authentication_status is None:
#         st.warning("Please enter your username and password")
#     st.session_state["authenticator"] = authenticator


# def logout():
#     authenticator.logout("Logout", "main")
#     del st.session_state["authenticator"]
#     time.sleep(0.1)


# def logout_button():
#     return st.button("Logout", on_click=logout)
