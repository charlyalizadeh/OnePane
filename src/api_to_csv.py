import subprocess
import requests
import polars as pl

from config import * 
from connect.connect_microsoft_graph import get_graph_access_token


def api_to_csv_ad(out):
    powershell_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
    subprocess.call(
        f"./src/Import-CsvADComputers.ps1 -Out {out}",
        shell=True,
        executable=powershell_path
    )

def api_to_csv_intune(out):
    access_token = get_graph_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"
    response = requests.get(url, headers=headers)
    devices = response.json()
    df_data = {k:[] for k in devices["value"][0].keys()}
    for device in devices["value"]:
        for key, val in device.items():
            df_data[key].append(val)
    df = pl.DataFrame(df_data)
    df = df.drop(["deviceActionResults"])
    df.write_csv(out)

def api_to_csv_entra(out):
    access_token = get_graph_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = "https://graph.microsoft.com/v1.0/devices"
    response = requests.get(url, headers=headers)
    devices = response.json()
    df_data = {k:[] for k in devices["value"][0].keys()}
    for device in devices["value"]:
        for key, val in device.items():
            df_data[key].append(val)
    df = pl.DataFrame(df_data)
    df = df.drop(["physicalIds", "systemLabels", "extensionAttributes", "alternativeSecurityIds"])
    df.write_csv(out)

def api_to_csv_tenable_sensor(out):
    accessKey = CREDENTIALS["Tenable"]["accessKey"]
    secretKey = CREDENTIALS["Tenable"]["secretKey"]
    url = "https://cloud.tenable.com/scanners/null/agents?limit=1000"
    headers = {
        "accept": "application/json",
        "X-ApiKeys": f"accessKey={accessKey};secretKey={secretKey}"
    }
    response = requests.get(url, headers=headers).json()
    for i, agent in enumerate(response["agents"]):
        val = ""
        if "groups" in agent.keys():
            groups = agent["groups"]
            val = '|'.join([f"name:{g['name']};id:{g['id']}" for g in groups])
        response["agents"][i]["groups"] = val
    df = pl.from_dicts(response["agents"])
    df.write_csv(out)

def api_to_csv(source, out):
    if source == "ad":
        api_to_csv_ad(out)
    elif source == "intune":
        api_to_csv_intune(out)
    elif source == "endpoint":
        raise NotImplementedError("Automated importation for ManageEngine Endpoint Central is not implemented.")
    elif source == "entra":
        api_to_csv_entra(out)
    elif source == "tenable_sensor":
        api_to_csv_tenable_sensor(out)
