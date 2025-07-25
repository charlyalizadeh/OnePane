import polars as pl

from config import *
from clean import *
from imports.import_ad import import_ad
from imports.import_tenable import import_tenable_sensors
from imports.import_intune import import_intune
from imports.import_entra import import_entra
from write_excel import *
from process import *
from db import create_table_from_df, fill_table_from_df
from webapp.webapp import app


if __name__ == "__main__":
    # Automated import
    print("Importing AD Computer.")
    import_ad()
    print("Importing Intune devices.")
    import_intune()
    print("Importing ManageEngine Endpoint devices.")
    #import_endpoint() not automatized
    print("Importing Tenable sensor.")
    import_tenable_sensors()
    print("Import Entra ID device.")
    import_entra()

    # CSV import
    print("Reading data into CSV:")
    print("  - AD computer")
    df_ad = pl.read_csv(f'{PROJECT_PATH}/data/ADComputer.csv')
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
    df_ad = clean_df_ad(df_ad)
    df_intune = clean_df_intune(df_intune)
    df_endpoint = clean_df_endpoint(df_endpoint)
    df_tenable_sensor = clean_df_tenable_sensor(df_tenable_sensor)
    df_entra = clean_df_entra(df_entra)

    # Process
    print("Processing the data.")
    df_device = get_df_device(validity_rules, df_ad, df_intune, df_endpoint, df_tenable_sensor, df_entra)
    df_invalid = get_df_invalid(df_device, validity_rules)
    df_rules = get_df_rules(validity_rules)
    df_ad_duplicate = get_df_ad_duplicate(df_ad)
    df_intune_duplicate = get_df_intune_duplicate(df_intune)
    df_endpoint_duplicate = get_df_endpoint_duplicate(df_endpoint)
    df_tenable_sensor_duplicate = get_df_tenable_sensor_duplicate(df_tenable_sensor)
    df_entra_duplicate = get_df_entra_duplicate(df_entra)
    df_intune_duplicate_user = get_df_intune_duplicate_user(df_intune)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)

    cur = con.cursor()
    create_table_from_df(cur, df_ad, "ad_devices", unique=["device"])
    create_table_from_df(cur, df_intune, "intune_devices", unique=["id"])
    create_table_from_df(cur, df_endpoint, "endpoint_devices", unique=["serial_number"])
    create_table_from_df(cur, df_tenable_sensor, "tenable_sensor_devices", unique=["id"])
    create_table_from_df(cur, df_entra, "entra_devices", unique=["id"])
    fill_table_from_df(cur, df_ad, "ad_devices")
    fill_table_from_df(cur, df_intune, "intune_devices")
    fill_table_from_df(cur, df_endpoint, "endpoint_devices")
    fill_table_from_df(cur, df_tenable_sensor, "tenable_sensor_devices")
    fill_table_from_df(cur, df_entra, "entra_devices")
    con.commit()
    con.close()

    app.run(debug=True)
    # Export
    #print("Writing data to excel file.")
    #write_excel_all(
    #    df_device, df_invalid, df_rules,
    #    df_ad_duplicate, df_intune_duplicate, df_endpoint_duplicate, df_tenable_sensor_duplicate, df_entra_duplicate,
    #    df_intune_duplicate_user,
    #    "Device List"
    #)
