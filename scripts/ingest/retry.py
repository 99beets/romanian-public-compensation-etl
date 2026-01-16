import time
import random
from typing import Callable, TypeVar, Tuple

T = TypeVar("T")

def retry(
    fn: Callable[[], T],
    attempts: int = 3,
    base_delay_s: float = 1.0,
    max_delay_s: float = 10.0,
    retry_on: Tuple[type, ...] = (Exception,),
) -> T:
    
    """Retries a function call with exponential backoff.

    Args:
        fn: The function to be called.
        attempts: Number of attempts before giving up.
        base_delay_s: Base delay in seconds for backoff calculation.
        max_delay_s: Maximum delay in seconds between retries.
        retry_on: Tuple of exception types that should trigger a retry.

    Returns:
        The return value of the function if successful.

    Raises:
        The last exception raised by the function if all attempts fail.
    """
    last_err: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except retry_on as e:
            last_err = e
            if attempt == attempts:
                break
                
            # Exponential backoff with jitter
            delay = min(max_delay_s, base_delay_s * (2 ** (attempt - 1)))
            delay = delay + random.uniform(0, 0.25 * delay)

            print(f"[retry] attempt {attempt}/{attempts} failed: {e}. retrying in {delay:.1f}s...")
            time.sleep(delay)
    
    # If we get here, all attempts failed
    raise last_err