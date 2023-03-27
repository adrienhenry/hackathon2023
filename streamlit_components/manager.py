import streamlit as st
import os


def manager():
    st.write("This is the manager")

    if os.path.exists("data/scores.db"):
        with open("data/scores.db", "rb") as file:
            btn = st.download_button(
                label="Download score database",
                data=file,
                file_name="scores.db",
                mime="application/octet-stream",
            )

    with st.form("score-form", clear_on_submit=True):
        uploaded_file = st.file_uploader("Upload your db", accept_multiple_files=False)
        submitted = st.form_submit_button("Upload")
        if submitted:
            with open("data/scores.db", "wb") as file:
                file.write(uploaded_file.getbuffer())
            st.success("Database updated")
