from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent.resolve()
CHROME_DATA_PATH = Path("~/AppData/Local/Google/Chrome").expanduser()
CHROME_EX_PATH = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
DEFAULT_CHROME_PROFILE_PATH = CHROME_DATA_PATH / "User Data/Default"
PROJECT_CHROME_PROFILE_PATH = PROJECT_PATH / ".profile"
PROJECT_CHROME_PROFILE_NAME = "Selenium"

validity_rules = {
    "LAPTOP_FR":              {"ad_computer": True,  "intune": True,  "endpoint": True,  "tenable_sensor": True,  "entra": True},
    "LAPTOP_RO":              {"ad_computer": True,  "intune": True,  "endpoint": True,  "tenable_sensor": True,  "entra": True},
    "Windows VM":             {"ad_computer": True,  "intune": True,  "endpoint": True,  "tenable_sensor": True,  "entra": True},
    "Windows Server":         {"ad_computer": True,  "intune": False, "endpoint": True,  "tenable_sensor": True,  "entra": False},
    "Windows Azure Server":   {"ad_computer": True,  "intune": False, "endpoint": True,  "tenable_sensor": False, "entra": False},
    "Arch":                   {"ad_computer": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": False},
    "Iphone":                 {"ad_computer": False, "intune": True,  "endpoint": False, "tenable_sensor": False, "entra": False},
    "Intaro":                 {"ad_computer": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": True},
    "Entra Device":           {"ad_computer": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": True},
    "Windows Autopilot":      {"ad_computer": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": True},
    "Old not renamed device": {"ad_computer": False, "intune": False, "endpoint": False, "tenable_sensor": False, "entra": False}
}
