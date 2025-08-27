from flask import Flask, render_template, make_response, jsonify, redirect, url_for, request
import sqlite3

from config import DB_PATH
from db import db_get_validity_rules_dict, db_get_modules, db_set_module_state
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
        return jsonify({'status': 'error', 'message': f'Error retriving category rules'}), 500

def get_df_device_safe(cur, validity_rules):
    #try:
    df_device = None
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    activated_modules = get_activated_modules()
    for module in activated_modules:
        module.load_data_from_db()
    category_rules = db_get_category_rules_dict(cur)
    validity_rules = db_get_validity_rules_dict(cur)
    con.close()
    df_device = join_devices_module(activated_modules, category_rules, validity_rules)
    #except:
    #    return jsonify({'status': 'error', 'message': f'Error retrieving all the devices'}), 500
    return df_device



# Modules
@app.route("/set_module_state/<module_name>/<state>")
def set_module_state(module_name, state):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    db_set_module_state(cur, module_name, int(state))
    con.commit()
    con.close()
    update_module(module_name)
    return redirect(url_for("modules"))

@app.route("/modules")
def modules():
    all_modules = get_all_modules()
    return render_template("modules.html", all_modules=all_modules)

# By tools
@app.route("/update_devices/<tab_id>")
def update_devices(tab_id):
    #try:
    if tab_id == "devices":
        update_activated_modules()
    else:
        update_module(tab_id)
    return jsonify({'status': 'success'}), 200
    #except:
    #    return jsonify({'status': 'error', 'message': f'Error calling the {tab_id} API'}), 500

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
    activated_modules = get_activated_modules()
    tables = [{
        "name": module.name,
        "display_name": module.display_name
    } for module in activated_modules]
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

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    db_update_category_rules(cur, rules)
    con.commit()
    con.close()
    return jsonify({'status': 'success'}), 200

@app.route("/set_category_rule/<category>/<regex>")
def set_category_rules(category, regex):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    db_set_category_rule(cur, category, regex)
    con.commit()
    con.close()
    return jsonify({'status': 'success'}), 200

# Validity rules
@app.route("/update_validity_rules", methods=['POST'])
def update_validity_rules():
    data = request.get_json()
    rules = data.get('rules', [])
    rules = [(r["category"], r["tool"], r["value"]) for r in rules]

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    db_update_validity_rules(cur, rules)
    con.commit()
    con.close()
    return jsonify({'status': 'success'}), 200

@app.route("/set_validity_rule/<category>/<tool>/<value>")
def set_validity_rule(category, tool, value):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    db_set_validity_rule(cur, category, tool, value)
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

    con.close()
    return make_response({'rows': df_device.rows()})

@app.route("/merged")
def merged():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    activated_modules = get_activated_modules()
    validity_rules = get_validity_rules_safe(cur)
    category_rules = get_category_rules_safe(cur)
    df_device = get_df_device_safe(cur, validity_rules)

    con.close()
    return render_template(
               "merged.html",
               colnames=df_device.columns,
               rows=df_device.rows(),
               category_rules=category_rules,
               validity_rules=validity_rules,
               activated_modules=activated_modules
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

# Single device
@app.route("/device/<name>")
def device(name):
    name = name.lower()
    activated_modules = get_activated_modules()
    activated_modules_dict = {module.name: module for module in activated_modules}
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    device_exist_in = db_device_exist_in(cur, name, activated_modules_dict.keys())
    device_serial_numbers = db_get_device_serial_numbers(cur, name, activated_modules_dict.keys())
    con.close()
    return render_template(
               "device.html",
               name=name,
               device_exist_in=device_exist_in,
               device_serial_numbers=device_serial_numbers,
               activated_modules_dict=activated_modules_dict
           )
