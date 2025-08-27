from datetime import datetime
import config
import keyword
import polars as pl
import re

# SQLite reserved keywords (simplified set)
SQLITE_RESERVED = {
    "ABORT", "ACTION", "ADD", "AFTER", "ALL", "ALTER", "ANALYZE", "AND", "AS", "ASC", "ATTACH", "AUTOINCREMENT",
    "BEFORE", "BEGIN", "BETWEEN", "BY", "CASCADE", "CASE", "CAST", "CHECK", "COLLATE", "COLUMN", "COMMIT", "CONFLICT",
    "CONSTRAINT", "CREATE", "CROSS", "CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP", "DATABASE", "DEFAULT", "DEFERRABLE",
    "DEFERRED", "DELETE", "DESC", "DETACH", "DISTINCT", "DROP", "EACH", "ELSE", "END", "ESCAPE", "EXCEPT", "EXCLUSIVE",
    "EXISTS", "EXPLAIN", "FAIL", "FOR", "FOREIGN", "FROM", "FULL", "GLOB", "GROUP", "HAVING", "IF", "IGNORE", "IMMEDIATE",
    "IN", "INDEX", "INDEXED", "INITIALLY", "INNER", "INSERT", "INSTEAD", "INTERSECT", "INTO", "IS", "ISNULL", "JOIN",
    "KEY", "LEFT", "LIKE", "LIMIT", "MATCH", "NATURAL", "NO", "NOT", "NOTNULL", "NULL", "OF", "OFFSET", "ON", "OR",
    "ORDER", "OUTER", "PLAN", "PRAGMA", "PRIMARY", "QUERY", "RAISE", "RECURSIVE", "REFERENCES", "REGEXP", "REINDEX",
    "RELEASE", "RENAME", "REPLACE", "RESTRICT", "RIGHT", "ROLLBACK", "ROW", "SAVEPOINT", "SELECT", "SET", "TABLE", "TEMP",
    "TEMPORARY", "THEN", "TO", "TRANSACTION", "TRIGGER", "UNION", "UNIQUE", "UPDATE", "USING", "VACUUM", "VALUES",
    "VIEW", "VIRTUAL", "WHEN", "WHERE", "WITH", "WITHOUT"
}

# Utilities
def _sanitize_sqlite_column_name(name):
    sanitized = re.sub(r'\W', '_', name)
    if re.match(r'^\d', sanitized):
        sanitized = '_' + sanitized
    if sanitized.upper() in SQLITE_RESERVED or keyword.iskeyword(sanitized.lower()):
        sanitized += "_col"
    return sanitized

def _polars_to_sqlite_type(pl_dtype):
    if pl_dtype == pl.Utf8:
        return "TEXT"
    elif pl_dtype in (pl.Int64, pl.Int32, pl.UInt32, pl.UInt64):
        return "INTEGER"
    elif pl_dtype in (pl.Float64, pl.Float32):
        return "REAL"
    elif pl_dtype == pl.Boolean:
        return "INTEGER"
    else:
        return "TEXT"

# Create tables
def db_create_table_from_df(cur, df, table, unique=[]):
    query = f"CREATE TABLE IF NOT EXISTS {table} (\n"
    for i, (coltype, col) in enumerate(zip(df.dtypes, df.columns)):
        sqlite_type = _polars_to_sqlite_type(coltype)
        col = _sanitize_sqlite_column_name(col)
        query += f"    {col} {sqlite_type}"
        if i < len(df.columns) - 1 or unique:
            query += ','
        query += '\n'
    for i, u in enumerate(unique):
        query += f"    UNIQUE ({','.join(u)})" 
        if i < len(unique) - 1:
            query += ','
        query += '\n'
    query += ");"
    cur.execute(query)

def db_create_table_modules(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            name TEXT,
            value INTEGER,
            UNIQUE(name)
        );
    """)

def db_create_table_category_rules(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category_rules (
            category TEXT,
            regex TEXT,
            UNIQUE(category)
        );
    """)

def db_create_table_validity_rules(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS validity_rules (
            category TEXT,
            module TEXT,
            value INTEGER,
            UNIQUE(category,module)
            FOREIGN KEY(category) REFERENCES category_rules(category) ON DELETE CASCADE
            FOREIGN KEY(module) REFERENCES modules(name) ON DELETE CASCADE
        );
    """)

def db_create_table_event(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS event_devices (
            type TEXT,
            device TEXT,
            source TEXT,
            date TEXT
        );
    """)


# Insert/Update data

## Modules
def db_fill_modules(cur, modules):
    modules = [(m, 0) for m in modules]
    insert_query = f"INSERT OR IGNORE INTO modules VALUES (?, ?)"
    cur.executemany(insert_query, modules)

def db_set_module_state(cur, module, state):
    query = f"UPDATE modules SET value = {state} WHERE name = '{module}'"
    cur.execute(query)

## Events
#TODO: not the most efficient, but for max 100 rows it doesn't matter
def db_insert_added_event(cur, df, table, col):
    query = f"SELECT {col}, device FROM {table}"
    cur.execute(query)
    rows = list(cur.fetchall())
    table_values = [row[0] for row in rows]
    table_values.sort()
    not_in_table = []
    date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    for col_val, device in zip(df[col], df["device"]):
        if col_val not in table_values:
            cur.execute(f"INSERT INTO event_devices VALUES('added', '{device}', '{table}', '{date}')")
            not_in_table.append([col_val, device])
    return not_in_table

def db_insert_deleted_event(cur, df, table, col):
    query = f"SELECT {col}, device FROM {table}"
    cur.execute(query)
    rows = list(cur.fetchall())
    df_values = df[col].to_list()
    not_in_df = []
    date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    for row in rows:
        if row[0] not in df_values:
            cur.execute(f"INSERT INTO event_devices VALUES('deleted', '{row[1]}', '{table}', '{date}')")
            not_in_df.append(row)
    return not_in_df

## Dataframe
def db_fill_table_from_df(cur, df, table):
    placeholders = ', '.join(["?"] * df.width)
    insert_query = f"INSERT OR REPLACE INTO {table} VALUES ({placeholders})"
    cur.executemany(insert_query, df.rows())

def db_update_table_from_df(cur, df, table, col):
    not_in_df = db_insert_deleted_event(cur, df, table, col)
    db_insert_added_event(cur, df, table, col)
    db_fill_table_from_df(cur, df, table)
    if not not_in_df:
        return
    if db_get_table_col_type(cur, table, col) == 'TEXT':
        not_in_df = [f"'{val[0]}'" for val in not_in_df]
    query = f"DELETE FROM {table} WHERE {col} IN ({','.join(not_in_df)})"
    cur.execute(query)

## Category rules
def db_update_category_rules(cur, rules):
    # Update and add new rules
    query = "INSERT OR REPLACE INTO category_rules VALUES (?, ?)"
    cur.executemany(query, rules)

    # Delete rules not present in `rules`
    pk = [f"'{rule[0]}'" for rule in rules]
    query = f"DELETE FROM category_rules WHERE category NOT IN ({','.join(pk)})"
    cur.execute(query)

    # Update validity rules
    db_update_validity_rules_from_category_rules(cur)

def db_set_category_rule(cur, category, regex):
    query = f"INSERT OR REPLACE INTO category_rules VALUES ('{category}', '{regex}')"
    cur.execute(query)

## Validity rules
def db_update_validity_rules(cur, rules):
    # Update and add new rules
    query = "INSERT INTO validity_rules VALUES (?, ?, ?)"
    cur.executemany(query, rules)

    # Delete rules not present in `rules`
    pk = [f"({rule[0]}, {rule[1]})" for rule in rules]
    query = f"DELETE FROM validity_rules WHERE (category, module) NOT IN ({','.join(pk)})"
    cur.execute(query)

def db_set_validity_rule(cur, category, module_name, value):
    query = f"INSERT OR REPLACE INTO validity_rules VALUES ('{category}', '{module_name}', {value})"
    cur.execute(query)

def db_update_validity_rules_from_category_rules(cur, module_names):
    category_rules = db_get_category_rules_dict(cur)
    validity_rules = db_get_validity_rules_dict(cur)
    for category in category_rules.keys():
        for module_name in module_names:
            if category not in validity_rules.keys() or module_name not in validity_rules[category].keys():
                print(f"Adding {category}, {module.name} = 2")
                db_set_validity_rule(cur, category, module_name, 2)


# Retrieve data
def db_get_df_from_table(cur, table, prefix=""):
    query = f"SELECT * FROM {table}"
    cur.execute(query)
    rows = cur.fetchall()
    colnames = [f"{prefix}{desc[0]}" for desc in cur.description]
    df = pl.from_records(rows, schema=colnames, orient="row")
    return df

def db_get_category_rules_dict(cur):
    query = "SELECT category, regex FROM category_rules"
    cur.execute(query)
    category_rules = {k:v for k, v in cur.fetchall()}
    return category_rules

def db_get_validity_rules_dict(cur):
    if not db_is_table(cur, "validity_rules"):
        create_table_validity_rules(cur)
    query = "SELECT category, module, value FROM validity_rules"
    cur.execute(query)
    rows = cur.fetchall()

    validity_rules = {}
    for row in rows:
        if row[0] not in validity_rules.keys():
            validity_rules[row[0]] = {}
        validity_rules[row[0]][row[1]] = row[2]
    return validity_rules

def db_get_modules(cur, value=[0, 1]):
    value = map(str, value)
    query = f"SELECT * FROM modules WHERE value in ({','.join(value)})"
    cur.execute(query)
    return cur.fetchall()

def db_get_table_col_names(cur, table):
    query = f"SELECT name FROM pragma_table_info('{table}');"
    cur.execute(query)
    return [row[0] for row in cur.fetchall()]

def db_get_table_col_types(cur, table, table_col):
    query = f"SELECT type FROM pragma_table_info('{table}') WHERE name = '{table_col}';"
    cur.execute(query)
    return cur.fetchone()[0]

def db_is_table(cur, table):
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    return cur.fetchall() != []

def db_is_table_empty(cur, table):
    if not db_is_table(cur, table):
        return True
    query = f"SELECT * FROM {table}"
    cur.execute(query)
    if not cur.fetchall():
        return True
    return False

def db_get_module_state(cur, module_name):
    query = f"SELECT value FROM modules WHERE name = '{module_name}'"
    cur.execute(query)
    return cur.fetchone()[0]

def db_device_exist_in(cur, device, module_names):
    subqueries = [f"EXISTS (SELECT 1 FROM {module_name} WHERE device = '{device}') AS in_{module_name}" for module_name in module_names]
    query = f"SELECT {','.join(subqueries)};"
    cur.execute(query)
    device_exist_in = {module_name: is_in for module_name, is_in in zip(module_names, cur.fetchall()[0])}
    return device_exist_in

def db_get_device_serial_numbers(cur, device, module_names):
    device_serial_numbers = {}
    for module_name in module_names:
        table_col_names = db_get_table_col_names(cur, module_name)
        if "serial_number" not in table_col_names:
            device_serial_numbers[module_name] = []
        else:
            query = f"SELECT serial_number FROM {module_name} WHERE device = '{device}'"
            cur.execute(query)
            device_serial_numbers[module_name] = [row[0] for row in cur.fetchall()]
    return device_serial_numbers
