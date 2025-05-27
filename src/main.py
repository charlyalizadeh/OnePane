import polars as pl
import xlsxwriter
import json

from write_excel import *
from process import *
from clean import clean_df



if __name__ == "__main__":
    # Import
    # The data are CSV extracted by hand on the different platforms
    # TODO: automate data import
    validity_rules = json.load(open("data/validity_rules.json", 'r'))
    df_intune = pl.read_csv('./data/Intune.csv')
    df_endpoint = pl.read_csv('./data/Endpoint.csv')
    df_tenable = pl.read_csv('./data/Tenable.csv')
    df_entra = pl.read_csv('./data/MicrosoftEntra.csv')

    # Clean
    df_intune, df_endpoint, df_tenable, df_entra = clean_df(df_intune, df_endpoint, df_tenable, df_entra)

    # Process
    df_device = get_df_device(validity_rules, df_intune, df_endpoint, df_tenable, df_entra)
    df_invalid = get_df_invalid(df_device, validity_rules)
    df_rules = get_df_rules(validity_rules)
    df_intune_duplicate = get_df_intune_duplicate(df_intune)
    df_endpoint_duplicate = get_df_endpoint_duplicate(df_endpoint)
    df_tenable_duplicate = get_df_tenable_duplicate(df_tenable)
    df_entra_duplicate = get_df_entra_duplicate(df_entra)

    # Export
    write_excel_all(
        df_device, df_invalid, df_rules,
        df_intune_duplicate, df_endpoint_duplicate, df_tenable_duplicate, df_entra_duplicate,
        "Device List"
    )
