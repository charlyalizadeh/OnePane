import sqlite3

from config import *
from db import *
from modules import *
from webapp.webapp import app


if __name__ == "__main__":
    dfs = {}

    print("Connecting to the sqlite database.")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    create_table_event(cur)
    create_table_validity_rules(cur)
    create_table_modules(cur)
    if is_table_empty(cur, "modules"):
        fill_modules(cur, [
            "ad_devices",
            "intune_devices",
            "entra_devices",
            "endpoint_devices",
            "tenable_sensor_devices"
        ])

    print("Commit and close connection.")
    con.commit()
    con.close()

    print("Running the Flask App")
    app.run(debug=True)
