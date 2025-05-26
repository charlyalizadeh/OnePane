import polars as pl
import xlsxwriter

from polars_utils import *
from validity import *


def get_df_device(validity_rules, df_intune, df_endpoint, df_tenable, df_entra):
    # Normalize the device column names
    df_intune = df_intune.rename({"Device name": "device"})
    df_endpoint = df_endpoint.rename({"Computer Name": "device"})
    df_tenable = df_tenable.rename({"display_fqdn": "device"})
    df_entra = df_entra.rename({"displayName": "device"})

    # Add prefix to column names to know where the data is from
    df_intune = add_prefix_column_names(df_intune, "intune_", ["device"])
    df_endpoint = add_prefix_column_names(df_endpoint, "endpoint_", ["device"])
    df_tenable = add_prefix_column_names(df_tenable, "tenable_", ["device"])
    df_entra = add_prefix_column_names(df_entra, "entra_", ["device"])

    # Add column to check for where the device is present
    df_intune = df_intune.with_columns(pl.Series(name="intune", values=[True] * df_intune.height))
    df_endpoint = df_endpoint.with_columns(pl.Series(name="endpoint", values=[True] * df_endpoint.height))
    df_tenable = df_tenable.with_columns(pl.Series(name="tenable", values=[True] * df_tenable.height))
    df_entra = df_entra.with_columns(pl.Series(name="entra", values=[True] * df_entra.height))

    # Normalize column names
    df_intune = fix_column_names(df_intune)
    df_endpoint = fix_column_names(df_endpoint)
    df_tenable = fix_column_names(df_tenable)
    df_entra = fix_column_names(df_entra)

    # Normalize devices name
    df_intune = df_intune.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    df_endpoint = df_endpoint.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    df_tenable = df_tenable.with_columns(pl.col("device").str.to_lowercase().str.split('.').list.first().alias("device"))
    df_entra = df_entra.with_columns(pl.col("device").str.to_lowercase().alias("device"))

    # Clean date data
    df_intune = df_intune.with_columns(
            (pl.col("intune_last_check-in").str.split('.').list.first().str.to_date(format="%Y-%m-%d %H:%M:%S")).alias("intune_last_check-in")
    )
    df_endpoint = df_endpoint.with_columns(
            (pl.col("endpoint_last_successful_scan").str.to_date(format="%b %d, %Y %I:%M %p")).alias("endpoint_last_successful_scan")
    )
    df_tenable = df_tenable.with_columns(
            (pl.col("tenable_first_observed").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%S")).alias("tenable_first_observed")
    )
    df_tenable = df_tenable.with_columns(
            (pl.col("tenable_last_observed").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%S")).alias("tenable_last_observed")
    )
    df_entra = df_entra.with_columns(
            (pl.col("entra_registrationtime").str.to_date(format="%Y-%m-%d %I:%M %p", strict=False)).alias("entra_registrationtime")
    )
    df_entra = df_entra.with_columns(
            (pl.col("entra_approximatelastsignindatetime").str.to_date(format="%Y-%m-%d %I:%M %p")).alias("entra_approximatelastsignindatetime")
    )

    # Join all the data
    df_device = df_intune.join(df_endpoint, on="device", how="full", coalesce=True)
    df_device = df_device.join(df_tenable, on="device", how="full", coalesce=True)
    df_device = df_device.join(df_entra, on="device", how="full", coalesce=True)

    # Put `false` in the appartenance column if the device is not in the software
    df_device = df_device.with_columns(
            (pl.col("intune").fill_null(False)),
            (pl.col("endpoint").fill_null(False)),
            (pl.col("tenable").fill_null(False)),
            (pl.col("entra").fill_null(False)),
    )

    # Add category
    df_device = df_device.with_columns((pl.col("device").map_elements(get_device_category)).alias("category"))

    # Add validity column
    # TODO: could be cleaner
    validity_rules_list = {k: [v["intune"], v["endpoint"], v["tenable"], v["entra"]] for k, v in validity_rules.items()}
    func1 = lambda row: check_device_validity(row, validity_rules_list)
    df_device = df_device.with_columns(pl.struct(pl.all()).map_elements(func1).alias("validity"))


    return df_device

def get_df_rules(validity_rules):
    categories = list(validity_rules.keys())
    dict_rules = {
            "category": categories,
            "intune": [v["intune"] for v in validity_rules.values()],
            "endpoint": [v["endpoint"] for v in validity_rules.values()],
            "tenable": [v["tenable"] for v in validity_rules.values()],
            "entra": [v["entra"] for v in validity_rules.values()]
    }
    df_rules = pl.DataFrame(dict_rules)

    return df_rules

def get_df_invalid(df_device, validity_rules):
    func2 = lambda row: get_invalidity_reason(row, validity_rules)
    df_invalid = df_device.with_columns(pl.struct(pl.all()).map_elements(func2).alias("invalidity_reason"))
    df_invalid = df_invalid.filter(pl.col("invalidity_reason") != "Valid")
    df_invalid = df_invalid.select(["device", "invalidity_reason"])

    return df_invalid

def get_df_entra_duplicate(df_entra):
    df_entra = df_entra.filter(pl.struct("displayName").is_duplicated())
    return df_entra
