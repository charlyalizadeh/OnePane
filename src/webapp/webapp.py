from flask import Flask, render_template, make_response, jsonify, redirect, url_for
import sqlite3

from config import DB_PATH, PROJECT_PATH
from db import get_df_from_table, get_validity_rules_dict
from api_to_csv import api_to_csv
from process import get_df_device


app = Flask(__name__)

# Utilities
def execute_query_safe(cur, query):
    try:
        cur.execute(query)
    except:
        return jsonify({'status': 'error', 'message': f'Error executing: {query}'}), 500

def get_validity_rules_safe(cur):
    try:
        validity_rules = get_validity_rules_dict(cur)
        return validity_rules
    except:
        return jsonify({'status': 'error', 'message': f'Error retriving validity rules'}), 500

def get_df_device_safe(cur, validity_rules):
    try:
        df_ad = get_df_from_table(cur, "ad_devices")
        df_intune = get_df_from_table(cur, "intune_devices")
        df_endpoint = get_df_from_table(cur, "endpoint_devices")
        df_tenable_sensor = get_df_from_table(cur, "tenable_sensor_devices")
        df_entra = get_df_from_table(cur, "entra_devices")
        validity_rules = get_validity_rules_dict(cur)
    except:
        return jsonify({'status': 'error', 'message': f'Error retriving all polars df from database'}), 500
    df_device = get_df_device(validity_rules, df_ad, df_intune, df_endpoint, df_tenable_sensor, df_entra)

    return df_device

# Per tools
@app.route("/update_devices/<tab_id>")
def update_devices(tab_id):
    try:
        api_to_csv(tab_id, PROJECT_PATH / f"data/{tab_id}_devices.csv")
        return jsonify({'status': 'success'}), 200
    except:
        return jsonify({'status': 'error', 'message': f'Error calling the {tab_id} API'}), 500

@app.route("/get_devices/<tab_id>")
def get_devices(tab_id):
    if tab_id == "devices":
        return redirect(url_for('get_all_devices'))

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Get the column names
    execute_query_safe(cur, f"SELECT name FROM pragma_table_info('{tab_id}_devices')")
    colnames = [r[0] for r in cur.fetchall()]
    device_index = colnames.index("device")

    # Get all devices and make the `device` column the first one
    execute_query_safe(cur, f"SELECT * FROM {tab_id}_devices")
    rows = []
    for j, row in enumerate(cur.fetchall()):
        row = list(row)
        row.insert(0, row.pop(device_index))
        rows.append(row)
        rows[j] = ['' if r is None else r for r in row]

    con.close()
    return make_response({'rows': rows})

@app.route("/split")
def split():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    tables = [
            {"table_name": "ad_devices", "name": "Active Directory"},
            {"table_name": "intune_devices", "name": "Intune"},
            {"table_name": "endpoint_devices", "name": "ManageEngine Endpoint"},
            {"table_name": "tenable_sensor_devices", "name": "Tenable Sensors"},
            {"table_name": "entra_devices", "name": "Entra ID"}
    ]
    for i, table in enumerate(tables):
        tables[i]["html_name"] = table["table_name"].replace("_devices", "")
        execute_query_safe(cur, f"SELECT name FROM pragma_table_info('{table['table_name']}')")
        colnames = [r[0] for r in cur.fetchall()]
        # Make the `device` column the first one
        colnames.remove("device")
        colnames = ["device"] + colnames
        tables[i]["colnames"] = colnames

    con.close()
    return render_template("split.html", tables=tables)

# All devices
@app.route("/get_all_devices")
def get_all_devices():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    validity_rules = get_validity_rules_safe(cur)
    df_device = get_df_device_safe(cur, validity_rules)

    return make_response({'rows': df_device.rows()})

@app.route("/merged")
def merged():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    validity_rules = get_validity_rules_safe(cur)
    df_device = get_df_device_safe(cur, validity_rules)

    return render_template(
               "merged.html",
               colnames=df_device.columns,
               rows=df_device.rows(),
               validity_rules=validity_rules
            )

@app.route("/set_validity_rule/<category>/<tool>/<value>")
def set_validity_rule(category, tool, value):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    execute_query_safe(cur, f"UPDATE validity_rules SET value = {int(value)} WHERE category = '{category}' AND tool = '{tool}'")
    con.commit()
    con.close()
    return jsonify({'status': 'success'}), 200

# Single device
@app.route("/device/<name>")
def device(name):
    name = name.lower()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    query = f"""
    SELECT ad.device, intune.device, endpoint.device, tenable_sensor.device, entra.device
    FROM ad_devices ad, intune_devices intune, endpoint_devices endpoint, tenable_sensors_devices tenable_sensor, entra_devices entra
    WHERE ad.device = '{name}'
    AND intune.device = '{name}'
    AND endpoint.device = '{name}'
    AND tenable.device = '{name}'
    AND entra.device = '{name}';
    """
    #query = f"""
    #SELECT ad.device, intune.device, endpoint.device
    #FROM ad_devices ad, intune_devices intune, endpoint_device en
    #WHERE ad.device = '{name}'
    #AND intune.device = '{name}'
    #"""
    print(query)
    execute_query_safe(cur, query)
    print(cur.fetchall())
    return jsonify({'status': 'success'}), 200

