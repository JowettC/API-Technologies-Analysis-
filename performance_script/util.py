import time
import requests
def measure_get_latency(url, port, num_requests=500):
    total_time = 0

    for _ in range(num_requests):
        start_time = time.time()
        response = requests.get(f"{url}{port}/users")
        end_time = time.time()

        # Ensure successful response
        if response.status_code == 200:
            total_time += (end_time - start_time)
        else:
            print(f"Failed request on port {port}")

    average_latency = total_time / num_requests
    return average_latency