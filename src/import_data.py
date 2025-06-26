import polars as pl
import subprocess
import requests
import json
import webbrowser

from config import * 


def import_ad_computer():
    powershell_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
    subprocess.call(
        "./src/Export-CsvADComputers.ps1",
        shell=True,
        executable=powershell_path
    )

def import_tenable_sensors(accessKey, secretKey):
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
    df.write_csv(PROJECT_PATH / "data/TenableSensor.csv")
