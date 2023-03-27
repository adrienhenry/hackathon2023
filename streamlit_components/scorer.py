import streamlit as st
import json
import plotly.express as px
import pandas as pd
import os


def with_write(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.write()

    return wrapper


class Scores:
    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            with open(filename) as f:
                self.scores = json.load(f)
        else:
            self.scores = {}

    def write(self):
        with open(self.filename, "w") as f:
            json.dump(self.scores, f)

    @with_write
    def add_score(self, user, score):
        if user in self.scores:
            self.scores[user].append(score)
        else:
            self.scores[user] = [score]

    def get_scores(self):
        return {key: pd.DataFrame(val) for key, val in self.scores.items()}

    def get_best_score(self):
        return {
            key: pd.DataFrame(val)["quality"].max() for key, val in self.scores.items()
        }


scores = Scores("data/scores.json")


def leaderboard():
    st.title("Leaderboard")
    best_scores = scores.get_best_score()
    best_scores = pd.DataFrame(best_scores, index=["quality"]).T.sort_values(
        "quality", ascending=False
    )
    print(best_scores)
    st.table(best_scores)


def plot_scores():
    user_scores = scores.get_scores()
    for user in user_scores:
        fig = px.scatter(user_scores[user], x="date", y="quality")
        st.plotly_chart(fig)


def score_tab():
    st.title("Score")
    leaderboard()
