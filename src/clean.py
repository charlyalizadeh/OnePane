import polars as pl


def fix_column_names(df, exclude=[]):
    rename_dict = {c:c.lower().replace(' ', '_').replace('-', '_') for c in df.columns if c not in exclude}
    return df.rename(rename_dict)

def clean_df_ad_computer(df_ad_computer):
    df_ad_computer = df_ad_computer.rename({"Name": "device"})
    df_ad_computer = fix_column_names(df_ad_computer)
    df_ad_computer = df_ad_computer.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    return df_ad_computer

def clean_df_intune(df_intune):
    df_intune = df_intune.rename({"Device name": "device"})
    df_intune = fix_column_names(df_intune)
    df_intune = df_intune.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    df_intune = df_intune.with_columns(
            (pl.col("last_check_in").str.split('.').list.first().str.to_date(format="%Y-%m-%d %H:%M:%S")).alias("last_check_in")
    )
    return df_intune

def clean_df_endpoint(df_endpoint):
    df_endpoint = df_endpoint.rename({"Computer Name": "device"})
    df_endpoint = fix_column_names(df_endpoint)
    df_endpoint = df_endpoint.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    df_endpoint = df_endpoint.with_columns(
            (pl.col("last_successful_scan").str.to_date(format="%b %d, %Y %I:%M %p")).alias("last_successful_scan")
    )
    return df_endpoint

def clean_df_tenable_sensor(df_tenable_sensor):
    df_tenable_sensor = df_tenable_sensor.rename({"Agent Name": "device"})
    df_tenable_sensor = fix_column_names(df_tenable_sensor)
    df_tenable_sensor = df_tenable_sensor.with_columns(pl.col("device").str.to_lowercase().str.split('.').list.first().alias("device"))
    df_tenable_sensor = df_tenable_sensor.with_columns(
            (pl.col("linked_on").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%S")).alias("linked_on")
    )
    df_tenable_sensor = df_tenable_sensor.with_columns(
            (pl.col("last_connect").str.split('.').list.first().str.to_date(format="%Y-%m-%dT%H:%M:%S")).alias("last_connect")
    )
    return df_tenable_sensor

def clean_df_entra(df_entra):
    df_entra = df_entra.rename({"displayName": "device"})
    df_entra = fix_column_names(df_entra)
    df_entra = df_entra.with_columns(pl.col("device").str.to_lowercase().alias("device"))
    df_entra = df_entra.with_columns(
            (pl.col("registrationtime").str.to_date(format="%Y-%m-%d %I:%M %p", strict=False)).alias("registrationtime")
    )
    df_entra = df_entra.with_columns(
            (pl.col("approximatelastsignindatetime").str.to_date(format="%Y-%m-%d %I:%M %p")).alias("approximatelastsignindatetime")
    )
    return df_entra

def clean_df(df_ad_computer, df_intune, df_endpoint, df_tenable_sensor, df_entra):
    df_ad_computer = clean_df_ad_computer(df_ad_computer)
    df_intune = clean_df_intune(df_intune)
    df_endpoint = clean_df_endpoint(df_endpoint)
    df_tenable_sensor = clean_df_tenable_sensor(df_tenable_sensor)
    df_entra = clean_df_entra(df_entra)
    return df_ad_computer, df_intune, df_endpoint, df_tenable_sensor, df_entra
