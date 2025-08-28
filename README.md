# OnePane

## Usage

### Credentials

Create a file named: `.credentials.json` and use the following templates:

```json
{
    "Tenable": {
        "accessKey": "<TENABLE_ACCESS_KEY>",
        "secretKey": "<TENABLE_SECRET_KEY>"
    },
    "Graph": {
        "tenantId": "<GRAPH_TENANT_ID>",
        "clientId": "<GRAPH_CLIENT_ID>",
        "clientSecret": "<GRAPH_CLIENT_SECRET>"
    }
}
```

### Run

```python
python -m venv .venv
.venv\Scripts\Activate.ps1 # or the specified way to activate python virutal env for your shell
python .\src\main.py
```

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
