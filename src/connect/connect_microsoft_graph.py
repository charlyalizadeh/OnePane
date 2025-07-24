import requests

import config


def get_graph_access_token():
    if config.GRAPH_ACCESS_TOKEN is None:
        set_graph_access_token()
    return config.GRAPH_ACCESS_TOKEN

def set_graph_access_token():
    tenantId = config.CREDENTIALS["Graph"]["tenantId"]
    clientId = config.CREDENTIALS["Graph"]["clientId"]
    clientSecret = config.CREDENTIALS["Graph"]["clientSecret"]
    url = f"https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token"
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": clientId,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": clientSecret,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    config.GRAPH_ACCESS_TOKEN = response.json()["access_token"]
