import polars as pl
import config
import re
import keyword

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

def sanitize_sqlite_column_name(name):
    sanitized = re.sub(r'\W', '_', name)
    if re.match(r'^\d', sanitized):
        sanitized = '_' + sanitized
    if sanitized.upper() in SQLITE_RESERVED or keyword.iskeyword(sanitized.lower()):
        sanitized += "_col"
    return sanitized

def polars_to_sqlite_type(pl_dtype):
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

def create_table_from_df(cur, df, name, unique=[]):
    query = f"CREATE TABLE IF NOT EXISTS {name} (\n"
    for i, (coltype, col) in enumerate(zip(df.dtypes, df.columns)):
        sqlite_type = polars_to_sqlite_type(coltype)
        col = sanitize_sqlite_column_name(col)
        query += f"    {col} {sqlite_type}"
        if col in unique:
            query += " UNIQUE"
        if i < len(df.columns) - 1:
            query += ','
        query += '\n'
    query += ");"
    cur.execute(query)

def fill_table_from_df(cur, df, name):
    placeholders = ', '.join(["?"] * df.width)
    insert_query = f"INSERT OR REPLACE INTO {name} VALUES ({placeholders})"
    cur.executemany(insert_query, df.rows())

def get_df_from_table(cur, name, prefix=""):
    query = f"SELECT * FROM {name}"
    cur.execute(query)
    rows = cur.fetchall()
    colnames = [f"{prefix}{desc[0]}" for desc in cur.description]
    df = pl.from_records(rows, schema=colnames, orient="row")
    return df

def create_table_event(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS devices_event (
            type TEXT,
            device TEXT,
            date TEXT
        );
    """)

def create_table_validity_rules(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS validity_rules (
                category TEXT,
                tool TEXT,
                value INTEGER,
                UNIQUE(category,tool)
        );
    """)

def fill_table_validity_rules_with_default(cur, force=False):
    values = []
    for category, table_dict in config.default_validity_rules.items():
        for table, value in table_dict.items():
            values.append([category, table, value])
    insert_query = ""
    if force:
        insert_query = "INSERT OR REPLACE INTO validity_rules VALUES (?, ?, ?)"
    else:
        insert_query = "INSERT OR IGNORE INTO validity_rules VALUES (?, ?, ?)"
    cur.executemany(insert_query, values)

def get_validity_rules_dict(cur):
    if not is_table(cur, "validity_rules"):
        create_table_validity_rules(cur)
        fill_table_validity_rules_with_default(cur)
    cur.execute("SELECT DISTINCT category FROM validity_rules")
    categories = cur.fetchall()
    if len(categories) != len(config.default_validity_rules):
        fill_table_validity_rules_with_default(cur)

    query = "SELECT category, tool, value FROM validity_rules"
    cur.execute(query)
    rows = cur.fetchall()

    validity_rules = {}
    for row in rows:
        if row[0] not in validity_rules.keys():
            validity_rules[row[0]] = {}
        validity_rules[row[0]][row[1]] = bool(row[2])
    return validity_rules

def is_table(cur, table):
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    return cur.fetchall() != []

def is_table_empty(cur, table):
    if not is_table(cur, table):
        return True
    query = f"SELECT * FROM {table}"
    cur.execute(query)
    if not cur.fetchall():
        return True
    return False
