import os
import sys
import argparse
import yaml
import sqlite3
import pandas as pd
import tqdm
from datetime import datetime
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)
from models.oven_api import OvenAPI
from streamlit_components.scorer import Scores

parser = argparse.ArgumentParser(description="Start the webservice.")
parser.add_argument("-p", "--param", type=str, help="Parameter file.")
parser.add_argument("-a", "--algo", type=str, help="Algo directory.", default="")
parser.add_argument("-u", "--user", type=str, help="user name.", default="")
args = parser.parse_args()
ALGO_PATH = os.path.abspath(args.algo)
sys.path.append(ALGO_PATH)
db_name = os.path.join(ALGO_PATH, "history.db")
filename = os.path.join(ALGO_PATH, "model.py")
from algo import run_reco

param = yaml.safe_load(open(os.path.join(PROJECT_ROOT, args.param), "r"))
model = OvenAPI(seed=param["seed"], param=param, db_name=db_name)

con = sqlite3.connect(db_name)
for i in range(param["nsteps"]):
    state = model.compute_next_state()
    history = pd.read_sql_query("SELECT * from history", con)
    state.update(run_reco(history))
    state = model.compute_outputs(state)
    model.simu_db.insert(state)
    with open(os.path.join(ALGO_PATH, "progress.txt"), "w") as f:
        f.write(f"{i / param['nsteps'] :.2f}")
sys.path.remove(ALGO_PATH)
df = pd.read_sql_query("SELECT * from history", con)

score = Scores(os.path.join(PROJECT_ROOT, "data/scores.db"))
score.add_score(
    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    args.user,
    df["quality"].iloc[param["warmup"] :].mean(),
)
