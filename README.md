# AXERIA Device Data Integrity Report

Project to check if the different device management tools have all our the AXERIA devices in them.

## Implemented tools

[x] ActiveDirectory
[ ] ManageEngine ActiveDirectory
[x] ManageEngine Endpoint
[ ] ManageEngine SFPOnDemand
[ ] OneDrive (SharePoint, OneDrive, Exchange)
[x] Intune
[x] Microsoft Entra
[x] Tenable

## Automated import tools

The following tools have automated data import (through their API)

[x] ActiveDirectory (`Get-ADComputer` PowerShell cmdlet)
[ ] ManageEngine ActiveDirectory
[ ] ManageEngine Endpoint
[ ] ManageEngine SFPOnDemand
[ ] OneDrive (SharePoint, OneDrive, Exchange)
[x] Intune (Graph API)
[x] Microsoft Entra (Graph API)
[x] Tenable (Tenable API)

## Implementation motivation

The implementation is not using OOP as a conscient choice.
Even though using OOP may help with maintainenace, I think it would decrease the readability.
Please, don't refactor this code using OOP except if you know what you are doing and have good motivation to do so.
