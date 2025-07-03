import subprocess

from config import * 


def import_ad_computer():
    powershell_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
    subprocess.call(
        "./src/imports/Import-CsvADComputers.ps1",
        shell=True,
        executable=powershell_path
    )
