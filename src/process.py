import polars as pl
import xlsxwriter

from validity import *


def add_prefix_column_names(df, prefix, exclude=[]):
    rename_dict = {c:f'{prefix}{c}' for c in df.columns if c not in exclude}
    return df.rename(rename_dict)

def get_df_device(validity_rules, df_intune, df_endpoint, df_tenable, df_entra):
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

    # Select desired columns
    df_device = df_device.select([
        "device", "category",
        "intune", "endpoint", "tenable", "entra",
        "intune_os", "intune_os_version",
        "endpoint_operating_system",  "endpoint_os_version",
        "tenable_display_operating_system",
        "entra_operatingsystem", "entra_operatingsystemversion",
        "intune_last_check_in", "intune_primary_user_display_name", 
        "endpoint_last_successful_scan",
        "tenable_first_observed", "tenable_last_observed", 
        "entra_registeredowners", "entra_registrationtime", "entra_approximatelastsignindatetime",
        "validity"
    ])


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

def get_df_intune_duplicate(df_intune):
    df_intune_duplicate = df_intune.filter(pl.struct("device").is_duplicated()).sort("device")
    df_intune_duplicate = df_intune_duplicate.select(["device", "primary_user_email_address", "last_check_in", "device_id"])
    return df_intune_duplicate

def get_df_endpoint_duplicate(df_endpoint):
    df_endpoint_duplicate = df_endpoint.filter(pl.struct("device").is_duplicated()).sort("device")
    df_endpoint_duplicate = df_endpoint_duplicate.select(["device", "last_successful_scan"])
    return df_endpoint_duplicate

def get_df_entra_duplicate(df_entra):
    df_entra_duplicate = df_entra.filter(pl.struct("device").is_duplicated()).sort("device")
    df_entra_duplicate = df_entra_duplicate.select(["device", "accountenabled", "registeredowners", "approximatelastsignindatetime", "objectid", "deviceid"])
    return df_entra_duplicate
