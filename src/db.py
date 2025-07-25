import polars as pl


def polars_to_sqlite_type(pl_dtype):
    if pl_dtype == pl.Utf8:
        return "TEXT"
    elif pl_dtype in (pl.Int64, pl.Int32, pl.UInt32, pl.UInt64):
        return "INTEGER"
    elif pl_dtype in (pl.Float64, pl.Float32):
        return "REAL"
    elif pl_dtype == pl.Boolean:
        return "INTEGER"  # SQLite stores booleans as 0/1
    else:
        return "TEXT"  # Could use DATE, but TEXT is more flexible

def create_table_from_df(cur, df, name, unique=[]):
    query = f"CREATE TABLE IF NOT EXISTS {name} (\n"
    for i, (coltype, col) in enumerate(zip(df.dtypes, df.columns)):
        sqlite_type = polars_to_sqlite_type(coltype)
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
    insert_query = f"INSERT OR IGNORE INTO {name} VALUES ({placeholders})"
    cur.executemany(insert_query, df.rows())

def get_df_from_table(cur, name, prefix=""):
    query = f"SELECT * FROM {name}"
    cur.execute(query)
    rows = cur.fetchall()
    colnames = [f"{prefix}{desc[0]}" for desc in cur.description]
    df = pl.from_records(rows, schema=colnames)
    return df

def create_table_event(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS devices_event (
            type TEXT,
            device TEXT
        );
    """)
