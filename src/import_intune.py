from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from pathlib import Path
import zipfile
import shutil

from chrome_webdriver import get_chrome_webdriver, connect_microsoft
from config import *


def check_intune_data_downloaded():
    download_path = Path.home() / "Downloads"
    files = download_path.glob('**/*')
    for f in files:
        if f.name.startswith("DevicesWithInventory"):
            return f
    return None

def go_to_all_device(driver):
    # Click "Device"
    device_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "_weave_e_58")))
    device_button.click()
    sleep(0.5)

    # Click "All Device"
    all_device_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-telemetryname="Menu-allDevices"]')))
    all_device_button.click()
    sleep(0.5)

def import_intune(driver):
    driver.get("https://intune.microsoft.com/#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/allDevices")
    try:
        cant_access_account = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "cantAccessAccount")))
        print("Connecting to Microsoft.")
        connect_microsoft(driver)
        driver.get("https://intune.microsoft.com/#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/allDevices")
    except:
        print("Already connected to microsoft.")


    # Switch to the Iframe
    iframe = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "AllManagedDevices.ReactView")))
    driver.switch_to.frame(iframe)
    sleep(0.5)

    # Click "Export"
    export_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class="ms-Button ms-Button--commandBar ms-CommandBarItem-link automation-id-export root-236"]')))
    export_button.click()
    sleep(0.5)

    # Click "Include all inventory data in the exported file"
    include_all_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Include all inventory data in the exported file')]")))
    include_all_button.click()
    sleep(0.5)

    # Yes button
    yes_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="button"][class="ms-Button ms-Button--primary root-289"][data-is-focusable="true"]')))
    yes_button.click()
    sleep(0.5)

    # Put the file in the right directory
    file = check_intune_data_downloaded()
    i = 0
    while not file:
        print(f"Searching for intune downloads{'.' * (i % 4)}{' ' * (3 - (i % 4))}", end="\r")
        file = check_intune_data_downloaded()
        if file:
            print(f"File found ({file}).")
        sleep(1)
        i += 1
    
    with zipfile.ZipFile(file, 'r') as zip_ref:
        data_path = Path(f"{PROJECT_PATH}/data")
        intune_path = data_path / "Intune.csv"
        csv_name = zip_ref.namelist()[0]
        print(f"Extracting:\n  {file.name}\\{csv_name}\n  -->\n  {data_path}\n")
        zip_ref.extractall(data_path)
        print(f"Moving:\n  {data_path}\\{csv_name}\n  -->\n  {intune_path}")
        csv_path = data_path / csv_name
        csv_path.replace(intune_path)
    print(f"Deleting {file}")
    file.unlink()
