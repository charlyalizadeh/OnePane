from flask import Flask, render_template, make_response, jsonify, redirect, url_for, request
import sqlite3

from config import DB_PATH
from db import getdb_validity_rules_dict, getdb_module, setdb_module_state
from modules import *


app = Flask(__name__)

# Utilities
def execute_query_safe(cur, query):
    try:
        cur.execute(query)
    except:
        return jsonify({'status': 'error', 'message': f'Error executing: {query}'}), 500

def get_validity_rules_safe(cur):
    try:
        validity_rules = getdb_validity_rules_dict(cur)
        return validity_rules
    except:
        return jsonify({'status': 'error', 'message': f'Error retriving validity rules'}), 500

def get_df_device_safe(cur, validity_rules):
    df_device = None
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        modules = [get_module(name[0]) for name in getdb_module(cur, [1])]
        validity_rules = getdb_validity_rules_dict(cur)
        df_device = join_devices_module(modules, validity_rules)
    except:
        return jsonify({'status': 'error', 'message': f'Error retriving all polars df from database'}), 500
    return df_device

# Per tools
@app.route("/update_devices/<tab_id>")
def update_devices(tab_id):
    try:
        module = get_module(tab_id)
        module.update()
        return jsonify({'status': 'success'}), 200
    except:
        return jsonify({'status': 'error', 'message': f'Error calling the {tab_id} API'}), 500

@app.route("/get_devices/<table_id>")
def get_devices(table_id):
    if table_id == "devices":
        return redirect(url_for('get_all_devices'))

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Get the column names
    table_name = table_id.replace('-', '_')
    execute_query_safe(cur, f"SELECT name FROM pragma_table_info('{table_name}')")
    colnames = [r[0] for r in cur.fetchall()]
    device_index = colnames.index("device")

    # Get all devices and make the `device` column the first one
    execute_query_safe(cur, f"SELECT * FROM {table_name}")
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
    modules = [get_module(name[0]) for name in getdb_module(cur, [1])]
    tables = [{
        "name": module.name,
        "display_name": module.display_name
    } for module in modules]
    for i, table in enumerate(tables):
        execute_query_safe(cur, f"SELECT name FROM pragma_table_info('{table['name']}')")
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

# Event
@app.route("/event_devices")
def event_devices():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    execute_query_safe(cur, "SELECT * FROM event_devices")
    rows = [list(row) for row in cur.fetchall()]
    for i in range(len(rows)):
        rows[i][0] = rows[i][0].capitalize()
        rows[i][2] = rows[i][2].replace("_devices", "").capitalize().replace("_", " ")
    con.close()
    return render_template(
               "events.html",
               events=rows
           )

@app.route("/set_module_state/<module>/<state>")
def set_module_state(module, state):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    setdb_module_state(cur, module, int(state))
    con.commit()
    con.close()
    return redirect(url_for("index"))

@app.route("/")
def index():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    module_activated = {row[0]: row[1] for row in getdb_module(cur, [0, 1])}
    modules = [get_module(key) for key in module_activated.keys()]
    if len(getdb_module(cur, [1])) >= 2:
        return redirect(url_for('merged'))
    return render_template("index.html", module_activated=module_activated, modules=modules)
