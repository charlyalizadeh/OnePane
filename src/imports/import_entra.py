import requests
import polars as pl

from config import *
from connect.connect_microsoft_graph import get_graph_access_token


def import_entra():
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
    df.write_csv(PROJECT_PATH / "data/MicrosoftEntra.csv")
