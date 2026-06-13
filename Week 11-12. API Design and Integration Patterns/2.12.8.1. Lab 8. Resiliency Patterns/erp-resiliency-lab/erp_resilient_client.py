import requests
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# --- LOGGING & ALERTING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

def trigger_alert(message):
    """Simulates sending a PagerDuty or Slack alert to DevOps"""
    logging.error(f" ALERT TRIGGERED: {message}")

# --- CIRCUIT BREAKER STATE MACHINE ---
class CircuitBreaker:
    def __init__(self, max_failures=3, reset_timeout_seconds=2):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout_seconds
        self.failures = 0
        self.state = "CLOSED" # CLOSED = Normal, OPEN = Failing Fast, HALF-OPEN = Testing recovery
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF-OPEN"
                logging.warning("Circuit is HALF-OPEN. Testing the connection...")
            else:
                raise Exception("Circuit Breaker is OPEN. Failing fast to protect system resources.")
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF-OPEN":
                logging.info("Service recovered. Circuit CLOSED.")
            self.state = "CLOSED"
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.max_failures and self.state != "OPEN":
                self.state = "OPEN"
                trigger_alert(f"Circuit Breaker TRIPPED. External service is down!")
            raise e
circuit = CircuitBreaker()

# --- RETRY STRATEGY (Exponential Backoff) ---
# Retry if it raises an Exception, stop after 3 attempts, wait 2^x seconds between tries
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10), reraise=True)
def make_api_request():
    start_time = time.time()
    
    # We set a strict 2-second timeout. If the API is slow (SLA breach), we drop it immediately!
    response = requests.get('http://flaky-api:5012/api/v1/credit-score', timeout=2.0)
    response.raise_for_status() # Treats 4xx and 5xx responses as exceptions
    
    duration = time.time() - start_time
    logging.info(f"API Call SUCCESS [Response Time: {duration:.2f}s]")
    return response.json()

# --- MAIN EXECUTION ---
def check_customer_credit():
    try:
        # We wrap the retrying function inside our Circuit Breaker
        result = circuit.call(make_api_request)
        print(f"--> ERP Business Logic: Approved with score {result['score']}\n")
    except Exception as e:
        logging.error(f"API Call FAILED completely: {e}\n")


if __name__ == '__main__':
    print("=== PHASE 1: Normal Operations (Expect some random backoff retries) ===")
    for i in range(5):
        time.sleep(1)
        check_customer_credit()
        
    print("=== PHASE 2: Simulating Total Outage ===")
    requests.post('http://flaky-api:5012/api/v1/crash-system')
    
    for i in range(5):
        time.sleep(1)
        check_customer_credit()

    print("=== PHASE 3: Simulating Recovery from Outage ===")
    requests.post('http://flaky-api:5012/api/v1/restore')
    
    for i in range(5):
        time.sleep(1)
        check_customer_credit()

