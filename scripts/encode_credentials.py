# %%
from loguru import logger
import yaml
import pickle as pkl
import streamlit_authenticator as stauth

CREDENTIAL_INPUT = "data/source_credentials.yaml"
CREDENTIAL_OUTPUT = "data/credentials.pkl"


credentials = yaml.load(open(CREDENTIAL_INPUT), Loader=yaml.SafeLoader)
logger.success(f"Loaded credentials from {CREDENTIAL_INPUT}")

for key in credentials["usernames"].keys():
    credentials["usernames"][key]["password"] = stauth.Hasher(
        [str(credentials["usernames"][key]["password"])]
    ).generate()[0]
with open(CREDENTIAL_OUTPUT, "wb") as f:
    pkl.dump(credentials, f)
logger.success(f"Saved hashed credentials to {CREDENTIAL_OUTPUT}")
