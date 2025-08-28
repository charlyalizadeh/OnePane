from pathlib import Path
import json
import sqlite3


# Editable
DB_PATH = Path("db/devices.db")

# Don't edit (or only if you know what you're doing)
PROJECT_PATH = Path(__file__).parent.parent.resolve()
CREDENTIALS = json.load(open(".credentials.json", "r"))
GRAPH_ACCESS_TOKEN = None
DB_CON = sqlite3.connect(DB_PATH, check_same_thread=False) 
DB_CON.execute("PRAGMA foreign_keys = 1")
