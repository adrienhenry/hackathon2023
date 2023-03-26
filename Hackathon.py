import streamlit as st
import numpy as np
import streamlit_authenticator as stauth
from streamlit_components import authentication
from loguru import logger
import os
import uuid

authentication.handle_login("data/credentials.pkl")


def upload_files(files):
    if len(files):
        path = os.path.join("temp", f"model_{uuid.uuid4()}")
        os.mkdir(path)
        for file in files:
            with open(os.path.join(path, file.name), "wb") as f:
                f.write(file.getbuffer())
                logger.success(f"Uploaded {file.name}")
        st.success("Model uploaded", icon="✅")
        return path


def simulator(path):
    from importlib.machinery import SourceFileLoader

    db_name = os.path.join(path, "history.db")
    filename = os.path.join(path, "model.py")
    algo = SourceFileLoader("algo", filename).load_module()
    # models.ovenapi.OvenAPI(seed=42, param="params.yaml", db_name=db_name)
    st.write(algo.run_reco({"a": 100, "b": 1}))


if authentication.handle_authentication_status():
    with st.form("my-form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Upload your model files", accept_multiple_files=True
        )
        submitted = st.form_submit_button("Upload")
        if submitted:
            path = upload_files(uploaded_files)
            simulator(path)
