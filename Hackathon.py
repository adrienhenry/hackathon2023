import streamlit as st
import numpy as np
import streamlit_authenticator as stauth
from streamlit_components import authentication, simulator

authentication.handle_login("data/credentials.pkl")


if authentication.handle_authentication_status():   
    simulator.simulation_tab()
