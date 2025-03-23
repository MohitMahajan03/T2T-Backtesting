import requests
import brotli
import json

# Define the endpoint URL
url = "https://www.nseindia.com/api/historical/foCPV?symbol=TCS&from=25-05-2024&to=23-06-2024&instrumentType=FUTSTK"

# Headers (NSE requires proper headers)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",  # Accept compressed responses
    "Referer": "https://www.nseindia.com",
}

try:
    # Send the GET request
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes

    # Decompress Brotli-encoded response
    if response.headers.get("Content-Encoding") == "br":
        decompressed_data = brotli.decompress(response.content)
        decoded_content = decompressed_data.decode("utf-8")  # Decode to string
        data = json.loads(decoded_content)  # Parse JSON
    else:
        # Fallback to JSON if no compression
        data = response.json()

    print(data)

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
except brotli.error as be:
    print("Error decompressing Brotli content:", be)
except json.JSONDecodeError as je:
    print("Error decoding JSON:", je)
except Exception as ex:
    print("An unexpected error occurred:", ex)
