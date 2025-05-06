import time
import requests

# Configuration
HTTP_SERVER = "http://localhost:8000"  # Replace with your actual server URL
INTERVAL = 0.5  # Time in seconds between requests

def check_status():
    url = f"{HTTP_SERVER}/status"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(f"[{time.ctime()}] Status: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"[{time.ctime()}] Error contacting {url}: {e}")

def main():
    while True:
        check_status()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
