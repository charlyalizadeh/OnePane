import subprocess
import polars as pl

from config import * 


def import_ad():
    powershell_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
    subprocess.call(
        "./src/imports/Import-CsvADComputers.ps1",
        shell=True,
        executable=powershell_path
    )
    df = pl.read_csv("data/ADComputer.csv")

