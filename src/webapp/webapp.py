from flask import Flask, render_template, make_response, jsonify, redirect, url_for, request

from db import db_get_validity_rules_dict, db_set_module_state
from modules import *


app = Flask(__name__)


# Utilities
def execute_query_safe(cur, query):
    try:
        cur.execute(query)
    except:
        return jsonify({'status': 'error', 'message': f'Error executing: {query}'}), 500

def get_validity_rules_dict_safe(cur):
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
    cur = DB_CON.cursor()

    df_device = None
    activated_modules = get_activated_modules()
    for module in activated_modules:
        module.load_data_from_db()
    category_rules = db_get_category_rules_dict(cur)
    validity_rules = db_get_validity_rules_dict(cur)
    df_device = join_devices_module(activated_modules, category_rules, validity_rules)

    cur.close()
    return df_device


# Modules
@app.route("/set_module_state/<module_name>/<state>")
def set_module_state(module_name, state):
    cur = DB_CON.cursor()

    db_set_module_state(cur, module_name, int(state))
    DB_CON.commit()
    update_module(module_name)

    cur.close()
    return redirect(url_for("modules"))

@app.route("/modules")
def modules():
    all_modules = get_all_modules()
    return render_template("modules.html", all_modules=all_modules)


# By tools
@app.route("/update_devices/<tab_id>")
def update_devices(tab_id):
    if tab_id == "devices":
        update_activated_modules()
    else:
        update_module(tab_id)
    return jsonify({'status': 'success'}), 200

@app.route("/get_devices/<table_id>")
def get_devices(table_id):
    if table_id == "devices":
        return redirect(url_for('get_all_devices'))

    cur = DB_CON.cursor()

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

    cur.close()
    return make_response({'rows': rows})

@app.route("/split")
def split():
    cur = DB_CON.cursor()

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

    cur.close()
    return render_template("split.html", tables=tables)

# Category rules
@app.route("/update_category_rules", methods=['POST'])
def update_category_rules():
    cur = DB_CON.cursor()

    data = request.get_json()
    rules = data.get('rules', [])
    db_update_category_rules(cur, rules)
    DB_CON.commit()
    
    cur.close()
    return jsonify({'status': 'success'}), 200

@app.route("/set_category_rule/<category>/<regex>")
def set_category_rules(category, regex):
    cur = DB_CON.cursor()

    db_set_category_rule(cur, category, regex)
    DB_CON.commit()

    cur.close()
    return jsonify({'status': 'success'}), 200

@app.route("/del_category_rule/<category>")
def del_category_rule(category):
    cur = DB_CON.cursor()

    db_del_category_rule(cur, category)
    DB_CON.commit()

    cur.close()
    return jsonify({'status': 'success'}), 200

# Validity rules
@app.route("/update_validity_rules", methods=['POST'])
def update_validity_rules():
    cur = DB_CON.cursor()

    data = request.get_json()
    rules = data.get('rules', [])
    rules = [(r["category"], r["tool"], r["value"]) for r in rules]
    db_update_validity_rules(cur, rules)
    DB_CON.commit()

    cur.close()
    return jsonify({'status': 'success'}), 200

@app.route("/set_validity_rule/<category>/<tool>/<value>")
def set_validity_rule(category, tool, value):
    cur = DB_CON.cursor()

    db_set_validity_rule(cur, category, tool, value)
    DB_CON.commit()

    cur.close()
    return jsonify({'status': 'success'}), 200

@app.route("/get_validity_rules")
def get_validity_rules():
    cur = DB_CON.cursor()

    activated_modules = [
        {
            "name": module.name,
            "display_name": module.display_name
        } for module in get_activated_modules()
    ]
    validity_rules = db_get_validity_rules_dict(cur)

    cur.close()
    return jsonify({'rules': validity_rules, 'activated_modules': activated_modules})


# All devices
@app.route("/get_all_devices")
def get_all_devices():
    cur = DB_CON.cursor()

    validity_rules = get_validity_rules_dict_safe(cur)
    df_device = get_df_device_safe(cur, validity_rules)

    cur.close()
    return make_response({'rows': df_device.rows()})

@app.route("/merged")
def merged():
    cur = DB_CON.cursor()

    activated_modules = get_activated_modules()
    for module in activated_modules:
        module.load_data_from_db()
    category_rules = get_category_rules_safe(cur)
    validity_rules = get_validity_rules_dict_safe(cur)
    df_device = get_df_device_safe(cur, validity_rules)

    cur.close()
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
    cur = DB_CON.cursor()

    execute_query_safe(cur, "SELECT * FROM event_devices")
    rows = [list(row) for row in cur.fetchall()]
    for i in range(len(rows)):
        rows[i][0] = rows[i][0].capitalize()
        rows[i][2] = rows[i][2].replace("_devices", "").capitalize().replace("_", " ")

    cur.close()
    return render_template(
               "events.html",
               events=rows
           )

# Single device
@app.route("/device/<name>")
def device(name):
    cur = DB_CON.cursor()

    name = name.lower()
    activated_modules = get_activated_modules()
    activated_modules_dict = {module.name: module for module in activated_modules}
    device_exist_in = db_device_exist_in(cur, name, activated_modules_dict.keys())
    device_serial_numbers = db_get_device_serial_numbers(cur, name, activated_modules_dict.keys())

    cur.close()
    return render_template(
               "device.html",
               name=name,
               device_exist_in=device_exist_in,
               device_serial_numbers=device_serial_numbers,
               activated_modules_dict=activated_modules_dict
           )
