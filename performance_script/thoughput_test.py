import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def measure_rps(url, num_requests=100, max_workers=20):
    """
    Measure the number of successful requests per second.
    """
    successful_requests = 0
    failed_requests = 0
    start_time = time.time()

    def make_request():
        try:
            response = requests.get(url, timeout=5)
            if 200 <= response.status_code < 300:
                return "success"
            else:
                return "fail"
        except Exception as e:
            print(f"Request failed with exception: {e}")
            return "exception"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        for future in as_completed(futures):
            result = future.result()
            if result == "success":
                successful_requests += 1
            else:
                failed_requests += 1

    end_time = time.time()
    duration = end_time - start_time
    # print(f"Successful requests: {successful_requests}")
    # print(f"Failed requests or exceptions: {failed_requests}")
    # print(f"Duration: {duration:.2f} seconds")
    return successful_requests / duration

def throughput_test(url, ports, labels):
    res = []
    for label, port in zip(labels, ports):
        api_url = f"{url}{port}/users"
        print(f"Testing throughput on {label} at {api_url}")
        # run 10 times then take the average
        
        average_rps = 0
        for i in range(10):
            rps = measure_rps(api_url)
            average_rps += rps
        average_rps = average_rps / 10
        res.append(average_rps)
    return res

if __name__ == "__main__":
    print(throughput_test("http://localhost:", [8022], ["Expressjs with graph"]))  # Example usage
