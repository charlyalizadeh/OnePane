import polars as pl
import xlsxwriter
import json

from write_excel import *
from process import *



if __name__ == "__main__":
    # Import data (CSV are extracted by hand on the different platforms)
    # TODO: automate data import
    validity_rules = json.load(open("data/validity_rules.json", 'r'))
    df_intune = pl.read_csv('./data/Intune.csv')
    df_endpoint = pl.read_csv('./data/Endpoint.csv')
    df_tenable = pl.read_csv('./data/Tenable.csv')
    df_entra = pl.read_csv('./data/MicrosoftEntra.csv')

    df_device = get_df_device(validity_rules, df_intune, df_endpoint, df_tenable, df_entra)
    df_invalid = get_df_invalid(df_device, validity_rules)
    df_rules = get_df_rules(validity_rules)
    #df_entra_duplicates = get_df_invalid(df_entra, validity_rules)

    # Select desired columns
    df_device = df_device.select([
        "device", "category",
        "intune", "endpoint", "tenable", "entra",
        "intune_os", "intune_os_version",
        "endpoint_operating_system",  "endpoint_os_version",
        "tenable_display_operating_system",
        "entra_operatingsystem", "entra_operatingsystemversion",
        "intune_last_check-in", "intune_primary_user_display_name", 
        "endpoint_last_successful_scan",
        "tenable_first_observed", "tenable_last_observed", 
        "entra_registeredowners", "entra_registrationtime", "entra_approximatelastsignindatetime",
        "validity"
    ])

    # Export
    write_excel_all(df_device, df_invalid, df_rules, "Device List")
