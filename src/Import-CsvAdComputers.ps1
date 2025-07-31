param (
    [String]$Out
)

if($PSVersionTable.PSVersion.Major -eq 5) {
    $csvStr = "Name,Enabled$([Environment]::NewLine)"
    $computers = Get-ADComputer -Filter * | Select Name,Enabled, IPv4Address
    $computers | % { 
        $csvStr += "$($_.Name),$($_.Enabled)"
        if($_ -ne $computers[-1]) {
            $csvStr += [Environment]::NewLine
        }
    }
    $csvStr | Out-File -FilePath $Out -Encoding ascii
}
else {
    Get-ADComputer -Filter * | `
        Select Name,Enabled | `
        Export-Csv -Path $Out -UseQuotes Never
}
