import polars as pl
import re

from validity import *

def add_prefix_column_names(df, prefix, exclude=[]):
    rename_dict = {c:f'{prefix}{c}' for c in df.columns if c not in exclude}
    return df.rename(rename_dict)

def join_devices_module(modules, category_rules, validity_rules):
    # Requires at least 2 modules
    if len(modules) == 0:
        return pl.DataFrame()

    # Add prefix
    dfs = {}
    for module in modules:
        dfs[module.name] = add_prefix_column_names(module.df, module.name, exclude=["device"])
        dfs[module.name] = dfs[module.name].with_columns(pl.Series(name=module.name, values=[True] * module.df.height))

    # Join all the data
    df_device = None
    for i, df in enumerate(dfs.values()):
        if i == 0:
            df_device = df
        else:
            df_device = df_device.join(df, on="device", how="full", coalesce=True)
    
    # Add category
    if category_rules:
        df_device = df_device.with_columns((pl.col("device").map_elements(get_device_category, return_dtype=pl.datatypes.String)).alias("category"))

    # Add validity column
    if category_rules and validity_rules:
        func1 = lambda row: check_device_validity(row, validity_rules)
        df_device = df_device.with_columns(pl.struct(pl.all()).map_elements(func1, return_dtype=pl.datatypes.Int8).alias("validity"))

    first_cols = ["device"] 
    if category_rules:
        first_cols += ["category"]
    first_cols += [module.name for module in modules]
    if validity_rules:
        first_cols += ["validity"]
    df_device = df_device.select(first_cols)

    # Select desired columns
    return df_device

def get_df_rules(validity_rules):
    categories = list(validity_rules.keys())
    dict_rules = {
            "category": categories,
            "ad": [v["ad"] for v in validity_rules.values()],
            "intune": [v["intune"] for v in validity_rules.values()],
            "endpoint": [v["endpoint"] for v in validity_rules.values()],
            "tenable_sensor": [v["tenable_sensor"] for v in validity_rules.values()],
            "entra": [v["entra"] for v in validity_rules.values()]
    }
    df_rules = pl.DataFrame(dict_rules)
    return df_rules

def set_column_names_space(df):
    rename_dict = {c:c.lower().replace(' ', '_').replace('-', '_') for c in df.columns}
    return df.rename(rename_dict)

def set_column_names_pascal_case(df):
    pattern = re.compile('[a-zA-Z][^A-Z]*')
    rename_dict = {}
    for col in df.columns:
        new_col = pattern.findall(col)
        new_col = '_'.join([c.lower() for c in new_col])
        rename_dict[col] = new_col
    return df.rename(rename_dict)
