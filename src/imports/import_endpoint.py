from time import sleep
from pathlib import Path
import requests
from bs4 import BeautifulSoup

from config import *


def check_endpoint_data_download():
    download_path = Path.home() / "Downloads"
    files = download_path.glob('**/*')
    for f in files:
        if f.name.startswith("InvComputersSummary"):
            return f
    return None

def import_endpoint():
    while True:
        response = requests.get("https://endpointcentral.manageengine.com/InvComputersSummary.csv?UNIQUE_ID=InvComputersSummary&fileName=InvComputersSummary&isExport=true&toolID=2102&selectedTab=Inventory")
        soup = BeautifulSoup(response.content)
        login_input = soup.find(id="login_id")
        if login_input:
            print("Please connect to ManageEngine Endpoint Central, the authentication is not automatised.")
            input("Press any key when it's done.")
        else:
            break
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
