param (
    [String]$Out
)

if($PSVersionTable.PSVersion.Major -eq 5) {
    Get-ADComputer -Filter * -Property * | ` 
        Select-Object * | `
        ConvertTo-Csv -NoTypeInformation -Delimiter ";" | `
        ForEach-Object { $_ -replace '"','' } | `
        Out-File -FilePath $Out -Encoding ASCII
}
else {
    Get-ADComputer -Filter * -Property * | Export-Csv -Path $Out -UseQuotes Never -Delimiter ;
}
