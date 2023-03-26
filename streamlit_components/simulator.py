import sys

sys.path.append("..")

from models.oven_api import OvenAPI


def simulator(path):
    from importlib.machinery import SourceFileLoader

    db_name = os.path.join(path, "history.db")
    filename = os.path.join(path, "model.py")
    algo = SourceFileLoader("algo", filename).load_module()
    # models.ovenapi.OvenAPI(seed=42, param="params.yaml", db_name=db_name)
    st.write(algo.run_reco({"a": 100, "b": 1}))
