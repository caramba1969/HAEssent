import urllib.request
import json

def main():
    url = "https://www.essent.nl/api/public/dynamicpricing/dynamic-prices/v1"
    headers = {
        "Accept": "application/json",
        "x-request-origin": "client"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        with open("api_response.json", "w") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
