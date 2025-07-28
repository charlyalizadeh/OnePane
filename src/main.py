import polars as pl
import sqlite3

from clean import *
from config import *
from db import *
from imports.import_ad import import_ad
from imports.import_entra import import_entra
from imports.import_intune import import_intune
from imports.import_tenable import import_tenable_sensors
from process import *
from webapp.webapp import app
from write_excel import *


if __name__ == "__main__":
    # Automated import
    print("Data importation:")
    print("  - AD Computer.")
    import_ad()
    print("  - Intune devices.")
    import_intune()
    #print("Importing ManageEngine Endpoint devices.")
    #import_endpoint() not automatized
    print("  - Tenable sensor.")
    import_tenable_sensors()
    print("  - Entra ID device.")
    import_entra()

    # Reading CSV data into polars DataFrame
    print("Reading data into CSV:")
    print("  - AD computer")
    df_ad = pl.read_csv(f'{PROJECT_PATH}/data/ADComputer.csv')
    print("  - Intune")
    df_intune = pl.read_csv(f'{PROJECT_PATH}/data/Intune.csv')
    print("  - ManageEngine Endpoint")
    df_endpoint = pl.read_csv(f'{PROJECT_PATH}/data/Endpoint.csv')
    print("  - Tenable Sensors")
    df_tenable_sensor = pl.read_csv(f'{PROJECT_PATH}/data/TenableSensor.csv')
    print("  - Entra ID")
    df_entra = pl.read_csv(f'{PROJECT_PATH}/data/MicrosoftEntra.csv')

    # Clean the DataFrames
    print("Cleaning the data:")
    print("  - AD computer")
    df_ad = clean_df_ad(df_ad)
    print("  - Intune")
    df_intune = clean_df_intune(df_intune)
    print("  - ManageEngine Endpoint")
    df_endpoint = clean_df_endpoint(df_endpoint)
    print("  - Tenable Sensors")
    df_tenable_sensor = clean_df_tenable_sensor(df_tenable_sensor)
    print("  - Entra ID")
    df_entra = clean_df_entra(df_entra)

    # Connect to the sqlite database
    print("Connecting to the sqlite database.")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Process
    print("Processing the data:")
    print("  - Query validity rules")
    validity_rules = get_validity_rules_dict(cur)
    print("  - Merging all devices")
    df_device = get_df_device(validity_rules, df_ad, df_intune, df_endpoint, df_tenable_sensor, df_entra)

    # Create tables
    print("DB Operations:")
    print("  - Create tables if not exists:")
    print("    - ad_devices")
    create_table_from_df(cur, df_ad, "ad_devices", unique=["device"])
    print("    - intune_devices")
    create_table_from_df(cur, df_intune, "intune_devices", unique=["id"])
    print("    - endpoint_devices")
    create_table_from_df(cur, df_endpoint, "endpoint_devices", unique=["serial_number"])
    print("    - tenable_sensors_devices")
    create_table_from_df(cur, df_tenable_sensor, "tenable_sensor_devices", unique=["id"])
    print("    - entra_devices")
    create_table_from_df(cur, df_entra, "entra_devices", unique=["id"])

    # Insert data
    print("  - Insert data into the tables")
    print("    - ad_devices")
    fill_table_from_df(cur, df_ad, "ad_devices")
    print("    - intune_devices")
    fill_table_from_df(cur, df_intune, "intune_devices")
    print("    - endpoint_devices")
    fill_table_from_df(cur, df_endpoint, "endpoint_devices")
    print("    - tenable_sensor_devices")
    fill_table_from_df(cur, df_tenable_sensor, "tenable_sensor_devices")
    print("    - entra_devices")
    fill_table_from_df(cur, df_entra, "entra_devices")

    # Close connection
    print("Commit and close connection.")
    con.commit()
    con.close()

    # Run the webapp
    print("Running the Flask App")
    app.run(debug=True)
