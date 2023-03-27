import streamlit as st
import numpy as np
import streamlit_authenticator as stauth
from streamlit_components import authentication, simulator, scorer,manager

authentication.handle_login("data/credentials.pkl")


if authentication.handle_authentication_status():
    tab_simu, tab_score = st.tabs(["Simulation", "Scores"])
    with tab_simu:
        simulator.simulation_tab()
    with tab_score:
        scorer.score_tab()
    if st.session_state["username"]=="adrien":
        manager.manager()