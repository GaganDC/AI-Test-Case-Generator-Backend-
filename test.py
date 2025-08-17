import requests

owner = "GaganDC"
repo = "EXCELR-ASSIGNMENTS"
path = "AD- Converting text into features.ipynb"
token = "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"  # Use your actual token

url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
headers = {"Authorization": f"token {token}"}
resp = requests.get(url, headers=headers)
print("GitHub status:", resp.status_code)
print(resp.json())
