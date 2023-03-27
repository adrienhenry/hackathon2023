import streamlit as st
import os
from loguru import logger
import uuid
import sys
import subprocess
from streamlit_components.state_manager import HardStateManager
from streamlit_components.scorer import Scores
import plotly.express as px
import sqlite3
import shutil
import pandas as pd
import json
import datetime

state_manager = None
scores = Scores("data/scores.db")


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
    if state_manager.get_state("existing_model") is None:
        with st.form("my-form   ", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "Upload your model files", accept_multiple_files=True
            )
            submitted = st.form_submit_button("Upload")
            if submitted:
                path = upload_files(uploaded_files)
                state_manager.set_state("existing_model", path)

                logger.success(
                    "Model uploaded to {}".format(
                        state_manager.get_state("existing_model")
                    )
                )


def launch_model():

    subprocess.Popen(
        [
            f"{sys.executable}",
            "scripts/test_reco_algo.py",
            "-p",
            "params.yaml",
            "-a",
            state_manager.get_state("existing_model"),
            "-u",
            st.session_state["name"],
        ]
    )
    state_manager.set_state("model_launched", True)


def log_progrtest_reco_algo():
    global scores
    if state_manager.get_state("model_launched"):
        progress_file_path = os.path.join(
            state_manager.get_state("existing_model"), "progress.txt"
        )
        if os.path.exists(progress_file_path):
            with open(progress_file_path) as f:
                progress = float(f.read())
        else:
            progress = 0
        if progress == 1:
            date, quality = scores.get_last_user_score(st.session_state["name"])
            plot_results()
            st.write("Score(average quality): {0:.2f}".format(quality))
        else:
            st.progress(progress)


def run_model():
    if (
        state_manager.get_state("existing_model") is not None
        and state_manager.get_state("model_launched") is None
    ):
        st.button("Run model", on_click=launch_model, disabled=run_new_model_disabled())


def run_new_model_disabled():
    date, quality = scores.get_last_user_score(st.session_state["name"])
    if datetime.datetime.now() > date + datetime.timedelta(hours=1):
        return False
    else:
        st.warning(
            "You can't run a new model yet, wait until {}".format(
                (date + datetime.timedelta(hours=1)).strftime("%H:%M")
            )
        )
        return True


def simulation_tab():
    st.title("Simulation")
    global state_manager
    state_manager = HardStateManager(
        "data/{}_simulator.json".format(st.session_state["username"])
    )

    # st.write(st.session_state)
    algo_uploader()
    if state_manager.get_state("existing_model") is not None:
        st.button("Clear model", on_click=clear_model)
    run_model()
    log_progrtest_reco_algo()


def clear_model():
    if state_manager.get_state("existing_model") is not None:
        shutil.rmtree(state_manager.get_state("existing_model"))
        state_manager.clear_states()


def plot_results():
    if state_manager.get_state("existing_model") is not None:
        db_name = os.path.join(state_manager.get_state("existing_model"), "history.db")
        con = sqlite3.connect(db_name)
        df = pd.read_sql_query("SELECT * from history", con)
        fig = px.line(df, x="id", y="quality")
        st.plotly_chart(fig)
