import urllib.request

METRICS_URL = "http://localhost:8080/metrics"
ERROR_THRESHOLD = 0  # Alert if we see ANY 500 errors

def check_system_health():
    print(f"Monitoring APM Metrics at {METRICS_URL}...")
    try:
        response = urllib.request.urlopen(METRICS_URL)
        metrics_data = response.read().decode('utf-8')
        # Parse the Prometheus metrics looking for our 500 HTTP status counter
        error_count = 0
        for line in metrics_data.split('\n'):
            if 'http_requests_total' in line and 'http_status="500"' in line:
                # Example line: http_requests_total{endpoint="/api/crash",http_status="500",method="GET"} 1.0
                error_count += float(line.split(' ')[-1])
        if error_count > ERROR_THRESHOLD:
            print("\n[PAGERDUTY ALERT TRIGGERED]")
            print(f"CRITICAL: Detected {int(error_count)} Server Errors (HTTP 500)!")
            print("Action: Paging On-Call Engineer via SMS immediately.")
            print("--------------------------------------------------\n")
        else:
            print("System Health: Normal. Error rate within acceptable limits.")
    except Exception as e:
        print(f"Failed to reach metrics endpoint: {e}")

if __name__ == '__main__':
    check_system_health()

# podman build -t python-alert .
# podman run --name script -d python-alert  