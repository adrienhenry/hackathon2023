import streamlit as st
import os
from loguru import logger
import uuid
import sys
import subprocess
import time
from state_manager import HardStateManager

state_manager = None


def upload_files(files):
    if len(files):
        path = os.path.join(os.getcwd(), os.path.join("temp", f"model_{uuid.uuid4()}"))
        os.mkdir(path)
        for file in files:
            with open(os.path.join(path, file.name), "wb") as f:
                f.write(file.getbuffer())
                logger.success(f"Uploaded {file.name}")
        st.success("Model uploaded", icon="✅")
        return path


def algo_uploader():
    if st.session_state.get("existing_model", None) is None:
        with st.form("my-form", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "Upload your model files", accept_multiple_files=True
            )
            submitted = st.form_submit_button("Upload")
            if submitted:
                path = upload_files(uploaded_files)
                st.session_state["existing_model"] = path
                logger.success(
                    "Model uploaded to {}".format(st.session_state["existing_model"])
                )


def launch_model():

    subprocess.Popen(
        [
            f"{sys.executable}",
            "scripts/test_reco_algo.py",
            "-p",
            "params.yaml",
            "-a",
            st.session_state["existing_model"],
        ]
    )
    st.session_state["model_launched"] = True


def log_progrtest_reco_algo():
    if st.session_state.get("model_launched", False):
        progress_file_path = os.path.join(
            st.session_state["existing_model"], "progress.txt"
        )
        if os.path.exists(progress_file_path):
            with open(progress_file_path) as f:
                progress = float(f.read())
        else:
            progress = 0
        st.progress(progress)


def run_model():
    if "existing_model" in st.session_state and not st.session_state.get(
        "model_launched", False
    ):
        st.button("Run model", on_click=launch_model)


def simulation_tab():
    global state_manager
    state_manager = HardStateManager(
        "data/{}_simulator.json".format(st.session_state["username"])
    )
    st.write(st.session_state)
    algo_uploader()
    run_model()
    log_progrtest_reco_algo()
