import os

import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("IMGUR_CLIENT")
client_secret = os.getenv("IMGUR_SECRET")
headers = {"Authorization": f"Client-ID {client_id}"}
data = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials",
}
url = "https://api.imgur.com/oauth2/token"
response = requests.post(url, headers=headers, data=data)
response_json = response.json()
if "access_token" in response_json:
    bearer_token = response_json["access_token"]
    print(bearer_token)
else:
    print(f"Failed to generate bearer token: {response_json}")
