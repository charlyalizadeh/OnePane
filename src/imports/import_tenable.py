import polars as pl
import requests

from config import * 


def import_tenable_sensors():
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
    df.write_csv(PROJECT_PATH / "data/TenableSensor.csv")
