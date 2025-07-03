from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *
from getpass import getpass
import shutil
from time import sleep


def _get_chrome_webdriver_no_setup():
    options = webdriver.ChromeOptions()

    # Load profile
    options.add_argument(f"--user-data-dir={PROJECT_CHROME_PROFILE_PATH}")
    options.add_argument(f"--profile-directory={PROJECT_CHROME_PROFILE_NAME}")
    options.add_experimental_option("detach", True)

    # Remove unused logs
    options.add_argument("--log-level=1")
    options.add_argument("--no-sandbox")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=options)
    return driver

def get_chrome_webdriver():
    profile_path = PROJECT_CHROME_PROFILE_PATH / PROJECT_CHROME_PROFILE_NAME
    # If the chrome profile doesn't exists, setup the profile
    if not profile_path.is_dir():
        print(f"{profile_path} not found: Copying default chrome profile to {profile_path}")
        copy_chrome_default_profile()
    return _get_chrome_webdriver_no_setup()

def connect_microsoft(driver, url="https://intune.microsoft.com/"):
    email = input("Email: ")
    password = getpass()

    driver.get(url)

    # Mail
    email_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "i0116")))
    email_input.send_keys(email)
    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    submit_button.click()
    sleep(0.5)

    # Password
    password_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "i0118")))
    password_input.send_keys(password)
    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    submit_button.click()
    sleep(0.5)

    # Stay connected
    dont_display_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "KmsiCheckboxField")))
    dont_display_input.click()
    yes_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    yes_button.click()
    sleep(0.5)

    # Verify indentity
    text_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-value="OneWaySMS"]')))
    text_button.click()
    code = input("SMS code:")
    sleep(0.5)

    # Enter code
    code_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "idTxtBx_SAOTCC_OTC")))
    code_input.send_keys(code)
    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "idSubmit_SAOTCC_Continue")))
    submit_button.click()
    sleep(0.5)

    # Stay connected (again)
    try:
        yes_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        yes_button.click()
    except:
        pass

def connect_manageengine_endpoint(driver, url="https://endpointcentral.manageengine.com/webclient#/uems/home"):
    email = input("Email: ")
    driver.get(url)

    # Mail
    login_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "login_id")))
    login_input.send_keys(email)

    # Then use notification push (TODO: manage different connection method)

def copy_chrome_default_profile():
    profile_path = PROJECT_CHROME_PROFILE_PATH / PROJECT_CHROME_PROFILE_NAME

    # Create profile directory if not extists
    profile_path.mkdir(parents=True, exist_ok=True)

    # Copy the default profile to the project directory
    shutil.copytree(DEFAULT_CHROME_PROFILE_PATH, profile_path, dirs_exist_ok=True)
