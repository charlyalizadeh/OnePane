import polars as pl
from validity import *


def add_prefix_column_names(df, prefix, exclude=[]):
    rename_dict = {c:f'{prefix}{c}' for c in df.columns if c not in exclude}
    return df.rename(rename_dict)

def get_df_device(validity_rules, df_ad_computer, df_intune, df_endpoint, df_tenable_sensor, df_entra):
    # Add prefix to column names to know where the data is from
    df_ad_computer = add_prefix_column_names(df_ad_computer, "ad_computer_", ["device"])
    df_intune = add_prefix_column_names(df_intune, "intune_", ["device"])
    df_endpoint = add_prefix_column_names(df_endpoint, "endpoint_", ["device"])
    df_tenable_sensor = add_prefix_column_names(df_tenable_sensor, "tenable_sensor_", ["device"])
    df_entra = add_prefix_column_names(df_entra, "entra_", ["device"])

    # Add column to check for where the device is present
    df_ad_computer = df_ad_computer.with_columns(pl.Series(name="ad_computer", values=[True] * df_ad_computer.height))
    df_intune = df_intune.with_columns(pl.Series(name="intune", values=[True] * df_intune.height))
    df_endpoint = df_endpoint.with_columns(pl.Series(name="endpoint", values=[True] * df_endpoint.height))
    df_tenable_sensor = df_tenable_sensor.with_columns(pl.Series(name="tenable_sensor", values=[True] * df_tenable_sensor.height))
    df_entra = df_entra.with_columns(pl.Series(name="entra", values=[True] * df_entra.height))


    # Join all the data
    df_device = df_ad_computer.join(df_intune, on="device", how="full", coalesce=True)
    df_device = df_device.join(df_endpoint, on="device", how="full", coalesce=True)
    df_device = df_device.join(df_tenable_sensor, on="device", how="full", coalesce=True)
    df_device = df_device.join(df_entra, on="device", how="full", coalesce=True)

    # Put `false` in the appartenance column if the device is not in the software
    df_device = df_device.with_columns(
            (pl.col("ad_computer").fill_null(False)),
            (pl.col("intune").fill_null(False)),
            (pl.col("endpoint").fill_null(False)),
            (pl.col("tenable_sensor").fill_null(False)),
            (pl.col("entra").fill_null(False)),
    )

    # Add category
    df_device = df_device.with_columns((pl.col("device").map_elements(get_device_category)).alias("category"))

    # Add validity column
    # TODO: could be cleaner
    validity_rules_list = {k: [v["ad_computer"], v["intune"], v["endpoint"], v["tenable_sensor"], v["entra"]] for k, v in validity_rules.items()}
    func1 = lambda row: check_device_validity(row, validity_rules_list)
    df_device = df_device.with_columns(pl.struct(pl.all()).map_elements(func1).alias("validity"))

    # Select desired columns
    df_device = df_device.select([
        "device", "category",
        "ad_computer", "intune", "endpoint", "tenable_sensor", "entra",
        "endpoint_ip_address", "tenable_sensor_ip",
        "intune_operating_system", "intune_os_version",
        "endpoint_operating_system",  "endpoint_os_version",
        "tenable_sensor_platform",
        "entra_operating_system", "entra_operating_system_version",
        "intune_last_sync_date_time", "intune_email_address", 
        "endpoint_last_successful_scan",
        "tenable_sensor_linked_on", "tenable_sensor_last_connect", 
        "entra_registration_date_time", "entra_approximate_last_sign_in_date_time",
        "intune_serial_number", "endpoint_serial_number",
        "validity"
    ])
    return df_device

def get_df_rules(validity_rules):
    categories = list(validity_rules.keys())
    dict_rules = {
            "category": categories,
            "ad_computer": [v["ad_computer"] for v in validity_rules.values()],
            "intune": [v["intune"] for v in validity_rules.values()],
            "endpoint": [v["endpoint"] for v in validity_rules.values()],
            "tenable_sensor": [v["tenable_sensor"] for v in validity_rules.values()],
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

def get_df_ad_computer_duplicate(df_ad_computer):
    df_ad_computer_duplicate = df_ad_computer.filter(pl.struct("device").is_duplicated()).sort("device")
    return df_ad_computer_duplicate

def get_df_intune_duplicate(df_intune):
    df_intune_duplicate = df_intune.filter(pl.struct("device").is_duplicated()).sort("device")
    df_intune_duplicate = df_intune_duplicate.select(["device", "email_address", "last_sync_date_time", "id"])
    return df_intune_duplicate

def get_df_intune_duplicate_user(df_intune):
    df_intune_duplicate_user = df_intune.filter(pl.struct("user_principal_name").is_duplicated()).sort("user_principal_name")
    df_intune_duplicate_user = df_intune_duplicate_user.select(["device", "user_principal_name", "email_address", "last_sync_date_time", "id"])
    return df_intune_duplicate_user

def get_df_endpoint_duplicate(df_endpoint):
    df_endpoint_duplicate = df_endpoint.filter(pl.struct("device").is_duplicated()).sort("device")
    df_endpoint_duplicate = df_endpoint_duplicate.select(["device", "last_successful_scan"])
    return df_endpoint_duplicate

def get_df_tenable_sensor_duplicate(df_tenable_sensor):
    df_tenable_sensor_duplicate = df_tenable_sensor.filter(pl.struct("device").is_duplicated()).sort("device")
    df_tenable_sensor_duplicate = df_tenable_sensor_duplicate.select(["device", "last_connect"])
    return df_tenable_sensor_duplicate

def get_df_entra_duplicate(df_entra):
    df_entra_duplicate = df_entra.filter(pl.struct("device").is_duplicated()).sort("device")
    df_entra_duplicate = df_entra_duplicate.select(["device", "account_enabled", "approximate_last_sign_in_date_time", "id", "device_id"])
    return df_entra_duplicate
