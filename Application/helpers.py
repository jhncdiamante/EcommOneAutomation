MAX_ATTEMPTS = 3
import time

def retry_until_success(func, max_retries=MAX_ATTEMPTS, delay=2, exceptions=(Exception,), on_fail_message=None, on_fail_execute_message=None):
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            print(f"{on_fail_message or 'Attempt failed'}, retrying... ({attempt + 1}/{max_retries}) {e}")
            time.sleep(delay)
    raise Exception(on_fail_execute_message or "Max retries exceeded")