import requests
import time
from .retry import retry

URL = "https://jsonplaceholder.typicode.com/posts"  # placeholder public API

def fetch_posts():
    r = requests.get(URL, timeout=10)
    r.raise_for_status
    return r.json()

def main():
    print("Fetching sample API data...")
    data = retry(fetch_posts, attempts=3, base_delay_s=1.0)
    print(f"Fetched {len(data)} records from API")
    print("First record:", data[0])

if __name__ == "__main__":
    main()