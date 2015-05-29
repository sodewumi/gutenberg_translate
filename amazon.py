import requests

# urllib3.disable_warnings()
payload = {"format": "json", "isbn": "0486284735"}
response =requests.get("https://wwe.github.com")
print response.json()