from flask import Flask, render_template, make_response, jsonify, redirect, url_for, request
import sqlite3

from config import DB_PATH
from db import db_get_validity_rules_dict, db_get_module, db_set_module_state
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
        validity_rules = db_get_validity_rules_dict(cur)
        return validity_rules
    except:
        return jsonify({'status': 'error', 'message': f'Error retriving validity rules'}), 500

def get_category_rules_safe(cur):
    try:
        category_rules = db_get_category_rules_dict(cur)
        return category_rules
    except:
        return jsonify({'status': 'error', 'message': f'Error retriving validity rules'}), 500

def get_df_device_safe(cur, validity_rules):
    df_device = None
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    activated_modules = db_get_module(cur, [1])
    if not activated_modules:
        return pl.DataFrame()
    modules = [get_module(name[0]) for name in activated_modules]
    category_rules = db_get_category_rules_dict(cur)
    validity_rules = db_get_validity_rules_dict(cur)
    df_device = join_devices_module(modules, category_rules, validity_rules)
    return df_device

# Modules
@app.route("/set_module_state/<module>/<state>")
def set_module_state(module, state):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    db_set_module_state(cur, module, int(state))
    con.commit()
    con.close()
    get_module(module, api=True)
    return redirect(url_for("modules"))

@app.route("/modules")
def modules():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    all_modules = {row[0]: row[1] for row in db_get_module(cur, [0, 1])}
    modules = [get_module(key) for key in all_modules.keys()]
    return render_template("modules.html", all_modules=all_modules, modules=modules)

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
    modules = [get_module(name[0]) for name in db_get_module(cur, [1])]
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

# Category rules
@app.route("/update_category_rules", methods=['POST'])
def update_category_rules():
    data = request.get_json()
    rules = data.get('rules', [])
    rules = [(r["category"], r["regex"]) for r in rules]
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    db_update_category_rules(cur, rules)
    con.commit()
    return jsonify({'status': 'success'}), 200

@app.route("/set_category_rule/<category>/<regex>")
def set_category_rules():
    data = request.get_json()
    rules = data.get('rules', [])
    rules = [(r["category"], r["regex"]) for r in rules]
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    db_update_category_rules(cur, rules)
    con.commit()
    return jsonify({'status': 'success'}), 200


# Validity rules
@app.route("/set_validity_rule/<category>/<tool>/<value>")
def set_validity_rule(category, tool, value):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    execute_query_safe(cur, f"INSERT OR REPLACE INTO validity_rules VALUES(category, tool, value) VALUES ('{category}', '{tool}', {value})")
    con.commit()
    con.close()
    return jsonify({'status': 'success'}), 200

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
    category_rules = get_category_rules_safe(cur)
    df_device = get_df_device_safe(cur, validity_rules)

    return render_template(
               "merged.html",
               colnames=df_device.columns,
               rows=df_device.rows(),
               category_rules=category_rules,
               validity_rules=validity_rules
            )


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
