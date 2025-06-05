import polars as pl
import xlsxwriter
import json
import argparse

from write_excel import *
from process import *
from clean import clean_df
from import_data import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tenableAccessKey")
    parser.add_argument("tenableSecretKey")
    args = parser.parse_args()
    accessKey = args.tenableAccessKey
    secretKey = args.tenableSecretKey


    validity_rules = json.load(open("./data/validity_rules.json", 'r'))
    # Import
    # The data are CSV extracted by hand on the different platforms
    # TODO: automate data import

    # Create datafames
    import_ad_computer()
    df_ad_computer = pl.read_csv('./data/ADComputer.csv')
    df_intune = pl.read_csv('./data/Intune.csv')
    df_endpoint = pl.read_csv('./data/Endpoint.csv')
    df_tenable_sensor = import_tenable_sensors(accessKey, secretKey)
    df_entra = pl.read_csv('./data/MicrosoftEntra.csv')

    # Clean
    df_ad_computer, df_intune, df_endpoint, df_tenable_sensor, df_entra = clean_df(df_ad_computer, df_intune, df_endpoint, df_tenable_sensor, df_entra)

    # Process
    df_device = get_df_device(validity_rules, df_ad_computer, df_intune, df_endpoint, df_tenable_sensor, df_entra)
    df_invalid = get_df_invalid(df_device, validity_rules)
    df_rules = get_df_rules(validity_rules)
    df_ad_computer_duplicate = get_df_ad_computer_duplicate(df_ad_computer)
    df_intune_duplicate = get_df_intune_duplicate(df_intune)
    df_endpoint_duplicate = get_df_endpoint_duplicate(df_endpoint)
    df_tenable_sensor_duplicate = get_df_tenable_sensor_duplicate(df_tenable_sensor)
    df_entra_duplicate = get_df_entra_duplicate(df_entra)

    # Export
    write_excel_all(
        df_device, df_invalid, df_rules,
        df_ad_computer_duplicate, df_intune_duplicate, df_endpoint_duplicate, df_tenable_sensor_duplicate, df_entra_duplicate,
        "Device List"
    )
