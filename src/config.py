from pathlib import Path
import json

# Editable
DB_PATH = Path("db/devices.db")

# Don't edit (or only if you know what you're doing)
PROJECT_PATH = Path(__file__).parent.parent.resolve()
CREDENTIALS = json.load(open(".credentials.json", "r"))
GRAPH_ACCESS_TOKEN = None
