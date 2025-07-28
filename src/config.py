from pathlib import Path
import json

PROJECT_PATH = Path(__file__).parent.parent.resolve()
CHROME_DATA_PATH = Path("~/AppData/Local/Google/Chrome").expanduser()
CHROME_EX_PATH = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
DEFAULT_CHROME_PROFILE_PATH = CHROME_DATA_PATH / "User Data/Default"
PROJECT_CHROME_PROFILE_PATH = PROJECT_PATH / ".profile"
PROJECT_CHROME_PROFILE_NAME = "Selenium"

default_validity_rules = {
    "LAPTOP_FR":              {"ad": True,  "intune": True,  "endpoint": True,  "tenable_sensor": True,  "entra": True},
    "LAPTOP_RO":              {"ad": True,  "intune": True,  "endpoint": True,  "tenable_sensor": True,  "entra": True},
    "Windows VM":             {"ad": True,  "intune": True,  "endpoint": True,  "tenable_sensor": True,  "entra": True},
    "Windows Server":         {"ad": True,  "intune": False, "endpoint": True,  "tenable_sensor": True,  "entra": False},
    "Windows Azure Server":   {"ad": True,  "intune": False, "endpoint": True,  "tenable_sensor": False, "entra": False},
    "Arch":                   {"ad": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": False},
    "Iphone":                 {"ad": False, "intune": True,  "endpoint": False, "tenable_sensor": False, "entra": False},
    "Intaro":                 {"ad": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": True},
    "Entra Device":           {"ad": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": True},
    "Windows Autopilot":      {"ad": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": True},
    "Old not renamed device": {"ad": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": False}
}
CREDENTIALS = json.load(open(".credentials.json", "r"))
GRAPH_ACCESS_TOKEN = None

DB_PATH = Path("db/devices.db")
