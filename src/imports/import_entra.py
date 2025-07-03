from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from pathlib import Path
import datetime

from chrome_webdriver import connect_microsoft
from config import *

def check_entra_data_download():
    download_path = Path.home() / "Downloads"
    files = download_path.glob('**/*')
    for f in files:
        if f.name.startswith("exportDevice"):
            return f
    return None

def import_entra(driver):
    driver.get("https://entra.microsoft.com/#view/Microsoft_AAD_Devices/DevicesMenuBlade/~/Devices/menuId/Devices")
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "cantAccessAccount")))
        print("Connecting to Microsoft.")
        connect_microsoft(driver)
        driver.get("https://entra.microsoft.com/#view/Microsoft_AAD_Devices/DevicesMenuBlade/~/Devices/menuId/Devices")
    except:
        print("Already connected to microsoft.")
        

    # Switch Iframe
    iframe = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "DevicesList.ReactView")))
    driver.switch_to.frame(iframe)
    sleep(0.5)

    # Click "Export"
    export_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name="Download devices"]')))
    export_button.click()
    sleep(0.5)

    # Switch to mane content
    driver.switch_to.default_content()

    # Click "Start Download"
    start_download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[title="Start download"]')))
    start_download_button.click()
    sleep(0.5)

    # Go to device export
    driver.get("https://entra.microsoft.com/#view/Microsoft_AAD_IAM/TasksListBlade/asyncTaskType~/%5B%22DeviceExport%22%5D")

    # Get the first element in the device export table
    today = datetime.datetime.today().date()
    today_str = f"{today.year}-{today.month}-{today.day}"
    filename = f"exportDevice_{today_str}.csv"
    print(filename)
    last_row = WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, f'(//div[contains(text(), "{filename}")])[last()]')))
    last_row.click()

    # Click "Download results", ugly af
    i = 0
    downloaded = False
    while not downloaded:
        try:
            download_results_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[role="link"][class="fxs-fileDownloadLink"]')))
            download_results_button.click()
            downloaded = True
        except:
            print(f"Waiting for device export{'.' * (i % 4)}{' ' * (3 - (i % 4))}", end="\r")
            i += 1
            driver.refresh()

    file = check_entra_data_download()
    i = 0
    while not file:
        print(f"Searching for entra downloads{'.' * (i % 4)}{' ' * (3 - (i % 4))}", end="\r")
        file = check_entra_data_download()
        if file:
            print(f"File found ({file}).")
        sleep(1)
        i += 1
    entra_path = Path(f"{PROJECT_PATH}/data/MicrosoftEntra.csv")
    print(f"Moving:\n  ~/Downloads/{file}\n  -->\n  {entra_path}")
    file.replace(entra_path)
