import requests
import time

URL = "https://jsonplaceholder.typicode.com/posts"  # placeholder public API

def fetch_posts():
    r = requests.get(URL, timeout=10)
    r.raise_for_status
    return r.json()

def main():
    print("Fetching sample API data...")
    data = fetch_posts()
    print(f"Fetched {len(data)} records from API")
    print("First record:", data[0])

if __name__ == "__main__":
    main()