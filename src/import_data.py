import subprocess

def import_ad_computer():
    powershell_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
    subprocess.call(
        "./src/Export-CsvADComputers.ps1",
        shell=True,
        executable=powershell_path
    )
