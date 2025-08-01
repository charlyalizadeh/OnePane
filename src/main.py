import polars as pl
import sqlite3

from clean import *
from config import *
from db import *
from api_to_csv import api_to_csv
from process import *
from webapp.webapp import app
from write_excel import *


if __name__ == "__main__":
    sources = ["ad", "intune", "endpoint", "entra", "tenable_sensor"]
    unique = {
        "ad": [["device"]],
        "intune": [["managed_device_name"]],
        "endpoint": [["device"]],
        "tenable_sensor": [["uuid"], ["id"]],
        "entra": [["id"]]
    }
    dfs = {}

    print("Connecting to the sqlite database.")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    create_table_event(cur)
    create_table_validity_rules(cur)
    for source in sources:
        if len(unique[source][0]) != 1:
            raise ValueError(f"The first item of the unique values must be 1, got {len(unique[source][0])}")
        out = PROJECT_PATH / f"data/{source}_devices.csv"
        if source != "endpoint" and is_table_empty(cur, f"{source}_devices"):
            print(f"API Call: {source}")
            api_to_csv(source, out)
        dfs[source] = pl.read_csv(out)
        dfs[source] = clean_df(source, dfs[source])
        create_table_from_df(cur, dfs[source], f"{source}_devices", unique[source])
        update_table_from_df(cur, dfs[source], f"{source}_devices", unique[source][0][0])


    print("Query validity rules")
    validity_rules = get_validity_rules_dict(cur)
    print("Merging all devices")
    df_device = get_df_device(validity_rules, dfs["ad"], dfs["intune"], dfs["endpoint"], dfs["tenable_sensor"], dfs["entra"])

    print("Commit and close connection.")
    con.commit()
    con.close()

    print("Running the Flask App")
    app.run(debug=True)
