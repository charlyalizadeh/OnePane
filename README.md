# AXERIA Device Data Integrity Report

Project to check if the following directory/software have the same users/devices:

[ ] ActiveDirectory
[ ] ManageEngine ActiveDirectory
[x] ManageEngine Endpoint
[ ] OneDrive (SharePoint, OneDrive, Exchange)
[x] Intune
[x] Microsoft Entra
[x] Tenable

Ideally this program would extract the data automatically through their API.
This would requires giving this application rights to read a lot of AXERIA internal data.
So for the moment the data is extracted manually and imported in this program using export files.

## Implementation motivation

The implementation is not using OOP as a conscient choice.
Even though using OOP may help with maintainenace, I think it would decrease the readability.
Please, don't refactor this code using OOP except if you know what you are doing and have good motivation to do so.
