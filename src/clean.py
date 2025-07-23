import polars as pl
import re


def fix_column_names_space(df):
    rename_dict = {c:c.lower().replace(' ', '_').replace('-', '_') for c in df.columns}
    return df.rename(rename_dict)

def fix_column_names_pascal_case(df):
    pattern = re.compile('[a-zA-Z][^A-Z]*')
    rename_dict = {}
    for col in df.columns:
        new_col = pattern.findall(col)
        new_col = '_'.join([c.lower() for c in new_col])
        rename_dict[col] = new_col
    return df.rename(rename_dict)

def clean_df_ad_computer(df_ad_computer):
    df_ad_computer = df_ad_computer.rename({"Name": "device"})
    df_ad_computer = fix_column_names_space(df_ad_computer)
    df_ad_computer = df_ad_computer.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    return df_ad_computer

def clean_df_intune(df_intune):
    df_intune = df_intune.rename({"deviceName": "device"})
    df_intune = fix_column_names_pascal_case(df_intune)
    df_intune = df_intune.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    df_intune = df_intune.with_columns(
            (pl.col("last_sync_date_time").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%SZ")).alias("last_sync_date_time")
    )
    return df_intune

def clean_df_endpoint(df_endpoint):
    df_endpoint = df_endpoint.rename({"Computer Name": "device"})
    df_endpoint = fix_column_names_space(df_endpoint)
    df_endpoint = df_endpoint.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    df_endpoint = df_endpoint.with_columns(
            (pl.col("last_successful_scan").str.to_date(format="%b %d, %Y %I:%M %p")).alias("last_successful_scan")
    )
    return df_endpoint

def clean_df_tenable_sensor_csv(df_tenable_sensor):
    df_tenable_sensor = df_tenable_sensor.rename({"Agent Name": "device"})
    df_tenable_sensor = fix_column_names_space(df_tenable_sensor)
    df_tenable_sensor = df_tenable_sensor.with_columns(pl.col("device").str.to_lowercase().str.split('.').list.first().alias("device"))
    df_tenable_sensor = df_tenable_sensor.with_columns(
            (pl.col("linked_on").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%S")).alias("linked_on")
    )
    df_tenable_sensor = df_tenable_sensor.with_columns(
            (pl.col("last_connect").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%S")).alias("last_connect")
    )
    return df_tenable_sensor

def clean_df_tenable_sensor(df_tenable_sensor):
    df_tenable_sensor = df_tenable_sensor.rename({"name": "device"})
    df_tenable_sensor = fix_column_names_space(df_tenable_sensor)
    df_tenable_sensor = df_tenable_sensor.with_columns(pl.col("device").str.to_lowercase())
    df_tenable_sensor = df_tenable_sensor.with_columns(pl.from_epoch("linked_on", time_unit="ms").alias("linked_on"))
    df_tenable_sensor = df_tenable_sensor.with_columns(pl.from_epoch("last_connect", time_unit="ms").alias("last_connect"))
    df_tenable_sensor = df_tenable_sensor.with_columns(pl.from_epoch("last_scanned", time_unit="ms").alias("last_scanned"))
    return df_tenable_sensor

def clean_df_entra(df_entra):
    df_entra = df_entra.rename({"displayName": "device"})
    df_entra = fix_column_names_pascal_case(df_entra)
    df_entra = df_entra.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    #2024-12-27T19:19:23Z
    df_entra = df_entra.with_columns(
            (pl.col("registration_date_time") \
               .str.replace("T", " ", literal=True) \
               .str.replace("Z", " ", literal=True) \
               .str.to_date(format="%Y-%m-%d %H:%M:%S", strict=False)) \
               .alias("registration_date_time")
    )
    df_entra = df_entra.with_columns(
            (pl.col("approximate_last_sign_in_date_time") \
               .str.replace("T", " ", literal=True) \
               .str.replace("Z", " ", literal=True) \
               .str.to_date(format="%Y-%m-%d %H:%M:%S", strict=False)) \
               .alias("approximate_last_sign_in_date_time")
    )
    return df_entra
