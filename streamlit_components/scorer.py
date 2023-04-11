import streamlit as st
import json
import plotly.express as px
import pandas as pd
import os
import sqlite3
import datetime

DATE_TIME_FORMAT = "%d/%m/%Y %H:%M:%S"


def with_connection(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        self._con = sqlite3.connect(self.filename, check_same_thread=False)
        result = func(*args, **kwargs)
        self._con.close()
        return result

    return wrapper


class Scores:
    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            self._con = sqlite3.connect(filename, check_same_thread=False)
        else:
            self._con = sqlite3.connect(filename, check_same_thread=False)
            self.run_command(
                "CREATE TABLE scores(date TEXT PRIMARY KEY, user TEXT, score REAL)"
            )
        self._con.close()

    @with_connection
    def run_command(self, command, args=()):
        self._con.execute(command, args)
        self._con.commit()

    @with_connection
    def add_score(self, date, user, score):
        self.run_command(
            "INSERT OR IGNORE INTO scores VALUES (?, ?, ?)", (date, user, score)
        )

    @with_connection
    def get_scores(self):
        return pd.read_sql_query(
            "SELECT * from scores", self._con, parse_dates={"date": DATE_TIME_FORMAT}
        )

    @with_connection
    def get_best_score(self):
        best_scores = (
            self.get_scores()
            .groupby("user")
            .max()
            .sort_values("score", ascending=False)
        )
        return [(user, row["score"]) for user, row in best_scores.iterrows()]

    @with_connection
    def get_last_user_score(self, name):
        data = self._con.execute(
            "SELECT * from scores WHERE user = ?", (name,)
        ).fetchall()
        if len(data) == 0:
            return None, None
        return data
        data = data[0]
        return datetime.datetime.strptime(data[0], DATE_TIME_FORMAT), data[2]


scores = Scores("data/scores.db")


def leaderboard():
    st.title("Leaderboard")
    best_scores = scores.get_best_score()
    df = pd.DataFrame(best_scores)
    if len(best_scores) > 0:
        df.iloc[0, 0] = "{} {}".format("👑", df.iloc[0, 0])
        st.table(df.set_index(0).rename(columns={1: "Score"}))


def score_evolution():
    st.title("Score evolution")
    score_data = scores.get_scores()
    fig = px.scatter(score_data, x="date", y="score", color="user")
    fig.update_traces(marker=dict(size=10), selector=dict(mode="markers"))
    st.plotly_chart(fig)


def plot_scores():
    user_scores = scores.get_scores()
    for user in user_scores:
        fig = px.scatter(user_scores[user], x="date", y="quality")
        st.plotly_chart(fig)


def score_tab():
    st.title("Score")
    leaderboard()
    score_evolution()
