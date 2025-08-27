import polars as pl
from pathlib import Path
import sqlite3
import subprocess
import requests

from config import *
from process import *
from db import *
from connect.connect_microsoft_graph import get_graph_access_token


class DevicesModule:
    def __init__(self, source, display_source, name, display_name, unique_columns, update=False, **kwargs):
        self.object_category = "devices"
        self.source = source
        self.display_source = display_source
        self.name = name
        self.display_name = display_name
        self.unique_columns = unique_columns
        self.csv_path = PROJECT_PATH / f"data/{self.name}.csv"

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        if db_is_table_empty(cur, self.name):
            if update:
                self.update()
            else:
                try:
                    self.df = self.load_data_from_csv()
                except OSError as e:
                    print(f"[{self.display_name}]: Couldn't load data ({e})")
                    self.df = polars.DataFrame()
        else:
            self.load_data_from_db()
        con.close()

        assert len(self.unique_columns[0]) == 1

    def load_data_from_csv(self):
        print(f"[{self.display_name}]: Loading data from CSV file ({self.csv_path})")
        self.df = pl.read_csv(self.csv_path)

    def load_data_from_db(self):
        print(f"[{self.display_name}]: Loading data from database")
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        self.df = db_get_df_from_table(cur, self.name)
        con.close()

    def clean(self):
        print(f"[{self.display_name}]: Cleaning")
        pass

    def api_to_csv(self):
        print(f"[{self.display_name}]: API to CSV ({self.csv_path})")
        pass

    def update(self):
        try:
            self.api_to_csv()
        except NotImplementedError:
            print(f"[{self.display_name}]: API importation not implemented")
        self.load_data_from_csv()
        self.clean()

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        db_create_table_from_df(cur, self.df, self.name, self.unique_columns)
        db_update_table_from_df(cur, self.df, self.name, self.unique_columns[0][0])
        con.commit()
        con.close()


class ADDevicesModule(DevicesModule):
    def __init__(self, **kwargs):
        super().__init__("ad", "AD", "ad_devices", "AD devices", [["device"]], **kwargs)

    def clean(self):
        super().clean()
        self.df = self.df.rename({"Name": "device"})
        self.df = set_column_names_space(self.df)
        self.df = self.df.with_columns(pl.col("device").str.to_lowercase().alias("device"))

    def api_to_csv(self):
        super().api_to_csv()
        powershell_path = Path("C:\\ProgramFiles\\PowerShell\\7\\pwsh.exe")
        # If Powershell 7 is not installed we use Windows Powershell 5 (tho it's not the same software)
        if not powershell_path.is_file():
            powershell_path = Path('C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe')
        subprocess.call(
            f"./src/Import-CsvADComputers.ps1 -Out {self.csv_path}",
            shell=True,
            executable=powershell_path
        )

class IntuneDevicesModule(DevicesModule):
    def __init__(self, **kwargs):
        super().__init__("intune", "Intune", "intune_devices", "Intune devices", [["managed_device_name"]], **kwargs)

    def clean(self):
        super().clean()
        self.df = self.df.rename({"deviceName": "device"})
        self.df = set_column_names_pascal_case(self.df)
        self.df = self.df.with_columns(pl.col("device").str.to_lowercase().alias("device"))
        self.df = self.df.with_columns(
                (pl.col("last_sync_date_time").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%SZ")).alias("last_sync_date_time")
        )

    def api_to_csv(self):
        super().api_to_csv()
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
        df.write_csv(self.csv_path)

class EntraDevicesModule(DevicesModule):
    def __init__(self, **kwargs):
        super().__init__("entra", "Entra", "entra_devices", "Entra devices", [["id"]], **kwargs)

    def clean(self):
        super().clean()
        self.df = self.df.rename({"displayName": "device"})
        self.df = set_column_names_pascal_case(self.df)
        self.df = self.df.with_columns(pl.col("device").str.to_lowercase().alias("device"))
        self.df = self.df.with_columns(
                (pl.col("registration_date_time") \
                   .str.replace("T", " ", literal=True) \
                   .str.replace("Z", " ", literal=True) \
                   .str.to_date(format="%Y-%m-%d %H:%M:%S", strict=False)) \
                   .alias("registration_date_time")
        )
        self.df = self.df.with_columns(
                (pl.col("approximate_last_sign_in_date_time") \
                   .str.replace("T", " ", literal=True) \
                   .str.replace("Z", " ", literal=True) \
                   .str.to_date(format="%Y-%m-%d %H:%M:%S", strict=False)) \
                   .alias("approximate_last_sign_in_date_time")
        )

    def api_to_csv(self):
        super().api_to_csv()
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
        df.write_csv(self.csv_path)

class EndpointDevicesModule(DevicesModule):
    def __init__(self, **kwargs):
        super().__init__("endpoint", "Endpoint", "endpoint_devices", "Endpoint devices", [["device"]], **kwargs)

    def clean(self):
        super().clean()
        self.df = self.df.rename({"Computer Name": "device"})
        self.df = set_column_names_space(self.df)
        self.df = self.df.with_columns(pl.col("device").str.to_lowercase().alias("device"))
        self.df = self.df.with_columns(
                (pl.col("last_successful_scan").str.to_date(format="%b %d, %Y %I:%M %p")).alias("last_successful_scan")
        )

    def api_to_csv(self):
        super().api_to_csv()
        raise NotImplementedError("Automated importation for ManageEngine Endpoint Central is not implemented.")

class TenableSensorDevicesModule(DevicesModule):
    def __init__(self, **kwargs):
        super().__init__("tenable", "Tenable", "tenable_sensor_devices", "Tenable sensors devices", [["uuid"], ["id"]], **kwargs)

    def clean_csv(self):
        self.df = self.df.rename({"Agent Name": "device"})
        self.df = set_column_names_space(self.df)
        self.df = self.df.with_columns(pl.col("device").str.to_lowercase().str.split('.').list.first().alias("device"))
        self.df = self.df.with_columns(
                (pl.col("linked_on").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%S")).alias("linked_on")
        )
        self.df = self.df.with_columns(
                (pl.col("last_connect").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%S")).alias("last_connect")
        )

    def clean(self):
        super().clean()
        self.df = self.df.rename({"name": "device"})
        self.df = set_column_names_space(self.df)
        self.df = self.df.with_columns(pl.col("device").str.to_lowercase())
        self.df = self.df.with_columns(pl.from_epoch("linked_on", time_unit="ms").alias("linked_on"))
        self.df = self.df.with_columns(pl.from_epoch("last_connect", time_unit="ms").alias("last_connect"))
        self.df = self.df.with_columns(pl.from_epoch("last_scanned", time_unit="ms").alias("last_scanned"))

    def api_to_csv(self):
        super().api_to_csv()
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
        df.write_csv(self.csv_path)


def get_module(name, **kwargs):
    if name == "ad_devices":
        return ADDevicesModule(**kwargs)
    elif name == "intune_devices":
        return IntuneDevicesModule(**kwargs)
    elif name == "entra_devices":
        return EntraDevicesModule(**kwargs)
    elif name == "endpoint_devices":
        return EndpointDevicesModule(**kwargs)
    elif name == "tenable_sensor_devices":
        return TenableSensorDevicesModule(**kwargs)

def get_activated_modules(update=False, **kwargs):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    activated_modules = [get_module(row[0], update=update, **kwargs) for row in db_get_modules(cur, value=[1])]
    con.close()
    return activated_modules

def get_deactivated_modules(update=False, **kwargs):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    deactivated_modules = [get_module(row[0], update=update, **kwargs) for row in db_get_modules(cur, value=[0])]
    con.close()
    return deactivated_modules

def get_all_modules(update=False, **kwargs):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    all_modules = [get_module(row[0], update=update, **kwargs) for row in db_get_modules(cur, value=[0, 1])]
    con.close()
    return all_modules

def update_activated_modules():
    _ = get_activated_module(update=True)
