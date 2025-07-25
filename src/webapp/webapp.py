from flask import Flask, render_template, jsonify
import sqlite3
from pathlib import Path

from imports.import_ad import import_ad
from imports.import_tenable import import_tenable_sensors
from imports.import_intune import import_intune
from imports.import_entra import import_entra
from db import get_df_from_table
from config import validity_rules
from process import get_df_device


app = Flask(__name__)

DB_PATH = Path("db/devices.db")

@app.route('/refresh_tab/<tab_id>', methods=['POST'])
def refresh_tab(tab_id):
    print(f"Importing {tab_id} data")
    if tab_id == "ad":
        import_ad()
    elif tab_id == "intune":
        import_intune()
    elif tab_id == "tenable_sensors":
        import_tenable_sensors()
    elif tab_id == "entra":
        import_entra()
    return jsonify({"status": "success", "message": "Tab refreshed"})

@app.route("/merged")
def merged():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    df_ad = get_df_from_table(cur, "ad_devices")
    df_intune = get_df_from_table(cur, "intune_devices")
    df_endpoint = get_df_from_table(cur, "endpoint_devices")
    df_tenable_sensor = get_df_from_table(cur, "tenable_sensor_devices")
    df_entra = get_df_from_table(cur, "entra_devices")

    df_device = get_df_device(validity_rules, df_ad, df_intune, df_endpoint, df_tenable_sensor, df_entra)
    con.close()
    return render_template("merged.html", df=df_device)

@app.route("/split")
def split():
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()
    tables = [
            {"table_name": "ad_devices", "name": "Active Directory"},
            {"table_name": "intune_devices", "name": "Intune"},
            {"table_name": "endpoint_devices", "name": "ManageEngine Endpoint"},
            {"table_name": "tenable_sensor_devices", "name": "Tenable Sensors"},
            {"table_name": "entra_devices", "name": "Entra ID"}
    ]
    for i, table in enumerate(tables):
        tables[i]["html_name"] = table["table_name"].replace("_devices", "")
        c.execute(f"SELECT name FROM pragma_table_info('{table['table_name']}')")
        colnames = [r[0] for r in c.fetchall()]
        device_index = colnames.index("device")
        colnames.remove("device")
        colnames = ["device"] + colnames
        c.execute(f"SELECT * FROM {table['table_name']}")
        rows = [list(row) for row in c.fetchall()]
        for j, row in enumerate(rows):
            row[device_index], row[0] = row[0], row[device_index]
            rows[j] = ['' if r is None else r for r in row]
        tables[i]["rows"] = rows
        tables[i]["colnames"] = colnames
    return render_template("split.html", tables=tables)

@app.route("/validity_rules")
def validity_rules_view():
    return render_template("validity_rules.html")
