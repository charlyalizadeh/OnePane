import polars as pl
import xlsxwriter
import json
import argparse
from pathlib import Path
import sys

from write_excel import *
from process import *
from clean import clean_df
from import_data import *
from import_intune import *
from chrome_webdriver import get_chrome_webdriver
from config import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tenableAccessKey")
    parser.add_argument("tenableSecretKey")
    args = parser.parse_args()
    accessKey = args.tenableAccessKey
    secretKey = args.tenableSecretKey

    # Import
    # The data are CSV extracted by hand on the different platforms
    # TODO: automate data import

    # Automated import
    print("Importing AD Computer.")
    import_ad_computer()
    print("Importing Intune devices.")
    import_intune()
    print("Importing Tenable sensor.")
    import_tenable_sensors(accessKey, secretKey)

    # CSV import
    print("Reading data into CSV:")
    print("  - AD computer")
    df_ad_computer = pl.read_csv(f'{PROJECT_PATH}/data/ADComputer.csv')
    print("  - Intune devices")
    df_intune = pl.read_csv(f'{PROJECT_PATH}/data/Intune.csv')
    print("  - ManageEngine Endpoint")
    df_endpoint = pl.read_csv(f'{PROJECT_PATH}/data/Endpoint.csv')
    print("  - Tenable Sensors")
    df_tenable_sensor = pl.read_csv(f'{PROJECT_PATH}/data/TenableSensor.csv')
    print("  - Entra ID")
    df_entra = pl.read_csv(f'{PROJECT_PATH}/data/MicrosoftEntra.csv')

    # Clean
    print("Cleaning the data.")
    df_ad_computer, df_intune, df_endpoint, df_tenable_sensor, df_entra = clean_df(df_ad_computer, df_intune, df_endpoint, df_tenable_sensor, df_entra)

    # Process
    print("Processing the data.")
    df_device = get_df_device(validity_rules, df_ad_computer, df_intune, df_endpoint, df_tenable_sensor, df_entra)
    df_invalid = get_df_invalid(df_device, validity_rules)
    df_rules = get_df_rules(validity_rules)
    df_ad_computer_duplicate = get_df_ad_computer_duplicate(df_ad_computer)
    df_intune_duplicate = get_df_intune_duplicate(df_intune)
    df_endpoint_duplicate = get_df_endpoint_duplicate(df_endpoint)
    df_tenable_sensor_duplicate = get_df_tenable_sensor_duplicate(df_tenable_sensor)
    df_entra_duplicate = get_df_entra_duplicate(df_entra)
    df_intune_duplicate_user = get_df_intune_duplicate_user(df_intune)

    # Export
    print("Writing data to excel file.")
    write_excel_all(
        df_device, df_invalid, df_rules,
        df_ad_computer_duplicate, df_intune_duplicate, df_endpoint_duplicate, df_tenable_sensor_duplicate, df_entra_duplicate,
        df_intune_duplicate_user,
        "Device List"
    )
