from pathlib import Path
import json

PROJECT_PATH = Path(__file__).parent.parent.resolve()
CHROME_DATA_PATH = Path("~/AppData/Local/Google/Chrome").expanduser()
CHROME_EX_PATH = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
DEFAULT_CHROME_PROFILE_PATH = CHROME_DATA_PATH / "User Data/Default"
PROJECT_CHROME_PROFILE_PATH = PROJECT_PATH / ".profile"
PROJECT_CHROME_PROFILE_NAME = "Selenium"

default_validity_rules = {
    "LAPTOP_FR":              {"ad": 1,  "intune": 1,  "endpoint": 1,  "tenable_sensor": 1,  "entra": 1},
    "LAPTOP_RO":              {"ad": 1,  "intune": 1,  "endpoint": 1,  "tenable_sensor": 1,  "entra": 1},
    "Windows VM":             {"ad": 1,  "intune": 1,  "endpoint": 1,  "tenable_sensor": 1,  "entra": 1},
    "Windows Server":         {"ad": 1,  "intune": 0, "endpoint": 1,  "tenable_sensor": 1,  "entra": 0},
    "Windows Azure Server":   {"ad": 1,  "intune": 0, "endpoint": 1,  "tenable_sensor": 0, "entra": 0},
    "Arch":                   {"ad": 0, "intune": 0, "endpoint": 0, "tenable_sensor": 0, "entra": 0},
    "Iphone":                 {"ad": 0, "intune": 1,  "endpoint": 0, "tenable_sensor": 0, "entra": 0},
    "Intaro":                 {"ad": 0, "intune": 0, "endpoint": 0, "tenable_sensor": 0, "entra": 1},
    "Entra Device":           {"ad": 0, "intune": 0, "endpoint": 0, "tenable_sensor": 0, "entra": 1},
    "Windows Autopilot":      {"ad": 0, "intune": 0, "endpoint": 0, "tenable_sensor": 0, "entra": 1},
    "Old not renamed device": {"ad": 0, "intune": 0, "endpoint": 0, "tenable_sensor": 0, "entra": 0}
}
CREDENTIALS = json.load(open(".credentials.json", "r"))
GRAPH_ACCESS_TOKEN = None

DB_PATH = Path("db/devices.db")
