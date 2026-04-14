import requests
import time
from .retry import retry

URL = "https://jsonplaceholder.typicode.com/posts"  # placeholder public API

# Fetch data from external API.
# Raises an exception on HTTP errors so retry logic can handle failures.
def fetch_posts():
    r = requests.get(URL, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    print("Fetching sample API data...")

    # Retry wrapper adds basic resilience to transient API failures.
    data = retry(fetch_posts, attempts=3, base_delay_s=1.0)

    print(f"Fetched {len(data)} records from API")

    # Log a small sample instead of full record to avoid noisy output
    print("Sample record:", data[0])

    # Basic sanity check: ensure at least one record exists
    if not data:
        raise ValueError("No data returned from API")
    
    print("First record:", data[0])

if __name__ == "__main__":
    main()