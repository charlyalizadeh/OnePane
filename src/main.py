import sqlite3

from config import *
from db import *
from modules import *
from webapp.webapp import app


if __name__ == "__main__":
    dfs = {}

    print("Connecting to the sqlite database.")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    cur = DB_CON.cursor()

    db_create_table_event(cur)
    db_create_table_category_rules(cur)
    db_create_table_validity_rules(cur)
    db_create_table_modules(cur)
    if db_is_table_empty(cur, "modules"):
        db_fill_modules(cur, [
            "ad_devices",
            "intune_devices",
            "entra_devices",
            "endpoint_devices",
            "tenable_sensor_devices"
        ])

    print("Committing to the database.")
    DB_CON.commit()
    cur.close()

    print("Running the Flask App")
    app.run(debug=True)
