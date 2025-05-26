import polars as pl

def get_not_in(s1, s2):
    not_in = []
    for element in s2:
        if not series_contains(s1, element):
            not_in.append(element)
    return not_in

def series_contains(serie, value):
    return (serie == value).any()

def add_prefix_column_names(df, prefix, exclude=[]):
    rename_dict = {c:f'{prefix}{c}' for c in df.columns if c not in exclude}
    return df.rename(rename_dict)

def fix_column_names(df, exclude=[]):
    rename_dict = {c:c.lower().replace(' ', '_') for c in df.columns if c not in exclude}
    return df.rename(rename_dict)

def write_markdown(df, filename):
    with pl.Config() as cfg:
        cfg.set_tbl_formatting('ASCII_MARKDOWN')
        cfg.set_tbl_rows(-1)
        with open(filename, 'w') as f:
            print(df_all, file=f)
    
def print_columns_type(df):
    for col, coltype in zip(df.columns, df.dtypes):
        print(f"{col}: {coltype}")
