import polars as pl
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name
from datetime import datetime


def _get_condition_false(workbook):
    format_fg_red_bold = workbook.add_format({"font_color": "#9C0006", "bold": 1})
    condition_false = {
        "type": "cell",
        "criteria": "==",
        "value": "FALSE",
        "format": format_fg_red_bold
    }
    return condition_false

def _get_condition_true(workbook):
    format_fg_green_bold = workbook.add_format({"font_color": "#008000", "bold": 1}) # TRUE formatting
    condition_true = {
        "type": "cell",
        "criteria": "==",
        "value": "TRUE",
        "format": format_fg_green_bold
    }
    return condition_true



def write_excel_all(df_device, df_invalid, df_rules,
                    df_ad_computer_duplicate, df_intune_duplicate, df_endpoint_duplicate, df_tenable_sensor_duplicate, df_entra_duplicate,
                    worksheet_name="Device List"):
    today = datetime.today().strftime('%Y-%m-%d')
    with xlsxwriter.Workbook(f"./results/data_integrity_{today}.xlsx") as workbook:
        write_excel_device(workbook, df_device, worksheet_name)
        write_excel_invalid(workbook, df_invalid, worksheet_name)
        write_excel_rules(workbook, df_rules, worksheet_name)
        write_excel_ad_computer_duplicate(workbook, df_ad_computer_duplicate, worksheet_name)
        write_excel_intune_duplicate(workbook, df_intune_duplicate, worksheet_name)
        write_excel_endpoint_duplicate(workbook, df_endpoint_duplicate, worksheet_name)
        write_excel_tenable_sensor_duplicate(workbook, df_tenable_sensor_duplicate, worksheet_name)
        write_excel_entra_duplicate(workbook, df_entra_duplicate, worksheet_name)

def write_excel_device(workbook, df_device, worksheet_name):
    today = datetime.today().strftime('%Y-%m-%d')
    worksheet = workbook.add_worksheet(worksheet_name)

    condition_false = _get_condition_false(workbook)
    condition_true = _get_condition_true(workbook)
    format_bg_grey_italic = workbook.add_format({"bg_color": "#808080", "italic": 1}) # Duplicate formatting
    condition_duplicate = {
        "type": "duplicate",
        "format": format_bg_grey_italic
    }

    df_device.write_excel(
        workbook=workbook,
        worksheet=worksheet_name,
        table_style="Table Style Light 8",
        autofit=True,
        conditional_formats={
            "ad_computer": [condition_false, condition_true],
            "intune": [condition_false, condition_true],
            "endpoint": [condition_false, condition_true],
            "tenable_sensor": [condition_false, condition_true],
            "entra": [condition_false, condition_true],
            "device": condition_duplicate
        }
    )

    # Unvalid row conditional formatting is done outside of the
    # `write_excel` call because using excel cell range (ex: `$A$7:$B$10`)
    # doesn't seems to work in polars conditional formatting
    # TODO: make everything work with `write_excel`
    format_bg_red = workbook.add_format({"bg_color": "#F88379"}) # Unvalid row formatting
    condition_validity = {
        "type": "formula",
        "criteria": '=(INDIRECT("W"&ROW())=FALSE)*(INDIRECT("B"&ROW())<>"Not categorized")',
        "format": format_bg_red
    }
    last_cell = f"${xl_col_to_name(df_device.width - 1)}${df_device.height + 1}"
    worksheet.conditional_format(f"$A$1:{last_cell}", condition_validity)

    format_bg_mauve = workbook.add_format({ "bg_color": "#BA8888" }) # Uncategorized row formatting
    condition_not_categorized = {
        "type": "formula",
        "criteria": '=INDIRECT("B"&ROW())="Not categorized"',
        "format": format_bg_mauve
    }
    worksheet.conditional_format(f"$A$1:{last_cell}", condition_not_categorized)

def write_excel_invalid(workbook, df_invalid, worksheet_name):
    worksheet_name = f"{worksheet_name} invalid"
    worksheet = workbook.add_worksheet(worksheet_name)
    df_invalid.write_excel(
            workbook=workbook,
            worksheet=worksheet,
            table_style="Table Style Light 8",
            autofit=True
    )

def write_excel_rules(workbook, df_rules, worksheet_name):
    condition_false = _get_condition_false(workbook)
    condition_true = _get_condition_true(workbook)

    worksheet_name = f"{worksheet_name} validity rules"
    worksheet = workbook.add_worksheet(worksheet_name)
    df_rules.write_excel(
        workbook=workbook,
        worksheet=worksheet,
        table_style="Table Style Light 8",
        autofit=True,
        conditional_formats={
            "ad_computer": [condition_false, condition_true],
            "intune": [condition_false, condition_true],
            "endpoint": [condition_false, condition_true],
            "tenable_sensor": [condition_false, condition_true],
            "entra": [condition_false, condition_true]
        }
    )

def write_excel_ad_computer_duplicate(workbook, df_ad_computer_duplicate, worksheet_name):
    worksheet_name = f"ADComputer duplicate"
    worksheet = workbook.add_worksheet(worksheet_name)
    df_ad_computer_duplicate.write_excel(
        workbook=workbook,
        worksheet=worksheet,
        table_style="Table Style Light 8",
        autofit=True
    )

def write_excel_intune_duplicate(workbook, df_intune_duplicate, worksheet_name):
    worksheet_name = f"Intune duplicate"
    worksheet = workbook.add_worksheet(worksheet_name)
    df_intune_duplicate.write_excel(
        workbook=workbook,
        worksheet=worksheet,
        table_style="Table Style Light 8",
        autofit=True
    )

    format_bg_red = workbook.add_format({"bg_color": "#F88379"}) # Unvalid row formatting
    # Using OR condition somehow doesn't work.
    # (Just like AND, that's why I used the * operator in `write_excel_device`)
    condition_validity = {
        "type": "formula",
        "criteria": '=ISBLANK(INDIRECT("B"&ROW()))',
        "format": format_bg_red
    }
    last_cell = f"${xl_col_to_name(df_intune_duplicate.width - 1)}${df_intune_duplicate.height + 1}"
    worksheet.conditional_format(f"$A$1:{last_cell}", condition_validity)

def write_excel_endpoint_duplicate(workbook, df_endpoint_duplicate, worksheet_name):
    worksheet_name = f"Endpoint duplicate"
    worksheet = workbook.add_worksheet(worksheet_name)
    df_endpoint_duplicate.write_excel(
        workbook=workbook,
        worksheet=worksheet,
        table_style="Table Style Light 8",
        autofit=True
    )

def write_excel_tenable_sensor_duplicate(workbook, df_tenable_sensor_duplicate, worksheet_name):
    worksheet_name = f"Tenable Sensor duplicate"
    worksheet = workbook.add_worksheet(worksheet_name)
    df_tenable_sensor_duplicate.write_excel(
        workbook=workbook,
        worksheet=worksheet,
        table_style="Table Style Light 8",
        autofit=True
    )

def write_excel_entra_duplicate(workbook, df_entra_duplicate, worksheet_name):
    worksheet_name = f"Entra duplicate"
    worksheet = workbook.add_worksheet(worksheet_name)
    df_entra_duplicate.write_excel(
        workbook=workbook,
        worksheet=worksheet,
        table_style="Table Style Light 8",
        autofit=True
    )

    format_bg_red = workbook.add_format({"bg_color": "#F88379"}) # Unvalid row formatting
    # Using OR condition somehow doesn't work.
    # (Just like AND, that's why I used the * operator in `write_excel_device`)
    condition_validity1 = {
        "type": "formula",
        "criteria": '=INDIRECT("B"&ROW())=False',
        "format": format_bg_red
    }
    condition_validity2 = {
        "type": "formula",
        "criteria": '=ISBLANK(INDIRECT("C"&ROW()))',
        "format": format_bg_red
    }
    last_cell = f"${xl_col_to_name(df_entra_duplicate.width - 1)}${df_entra_duplicate.height + 1}"
    worksheet.conditional_format(f"$A$1:{last_cell}", condition_validity1)
    worksheet.conditional_format(f"$A$1:{last_cell}", condition_validity2)

