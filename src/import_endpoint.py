from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from pathlib import Path
import zipfile
import shutil
import requests

from chrome_webdriver import get_chrome_webdriver, connect_microsoft
from config import *


def check_endpoint_data_download():
    download_path = Path.home() / "Downloads"
    files = download_path.glob('**/*')
    for f in files:
        if f.name.startswith("InvComputersSummary"):
            return f
    return None

def import_endpoint(driver):
    driver.get("https://endpointcentral.manageengine.com/webclient#/uems/inventory/computers")
    try:
        signin_box = WebDriverWait(driver, 5).until(EC.element_be_clickable(By.ID, "login_id"))
        print("Connecting to ManageEngine Endpoint Central")
        connect_manageengine_endpoint(driver)
    except:
        print("Already connected to ManageEngine Endpoint Central")
    driver.get("https://endpointcentral.manageengine.com/InvComputersSummary.csv?UNIQUE_ID=InvComputersSummary&fileName=InvComputersSummary&isExport=true&toolID=2102&selectedTab=Inventory")
    file = check_endpoint_data_download()
    i = 0
    while not file:
        print(f"Searching for endpoint downloads{'.' * (i % 4)}{' ' * (3 - (i % 4))}", end="\r")
        file = check_endpoint_data_download()
        if file:
            print(f"File found ({file}).")
        sleep(1)
        i += 1
    endpoint_path = Path(f"{PROJECT_PATH}/data/Endpoint.csv") 
    print(f"Moving:\n  ~/Downloads/{file}\n  -->\n  {endpoint_path}")
    file.replace(endpoint_path)
