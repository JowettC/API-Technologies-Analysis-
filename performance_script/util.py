import time
import requests
def measure_get_latency(url, port, num_requests=5):
    total_time = 0

    for _ in range(num_requests):
        start_time = time.time()
        response = requests.get(f"{url}{port}/users")
        end_time = time.time()

        # Ensure successful response
        if response.status_code in [200, 201, 204]:
            total_time += (end_time - start_time)
        else:
            print(f"Failed request on port {port}")

    average_latency = total_time / num_requests
    return average_latency

def measure_post_latency(url, port, num_requests=5):
    total_time = 0
    for _ in range(num_requests):
        start_time = time.time()
        response = requests.post(f"{url}{port}/users", json={"username": "test", "email": "test_created@test.com"})
        end_time = time.time()
        # Ensure successful response
        if response.status_code in [200, 201, 204]:
            total_time += (end_time - start_time)
        else:
            print(response.status_code)
            print(response.text)
            print(f"Failed request on port {port}")
    
    average_latency = total_time / num_requests
    return average_latency
def measure_put_latency(url, port, num_requests=5):
    total_time = 0
    for i in range(num_requests):
        start_time = time.time()
        response = requests.put(f"{url}{port}/users/{i+51}", json={"username": "test", "email": "test_update@test.com"})
        end_time = time.time()
        # Ensure successful response
        if response.status_code  in [200, 201, 204]:
            total_time += (end_time - start_time)
        else:
            print(f"Failed request on port {port}")

    average_latency = total_time / num_requests
    return average_latency

def measure_delete_latency(url, port, start_num, num_requests=5):
    total_time = 0
    for i in range(num_requests):
        # print('start_num',start_num+i)
        start_time = time.time()
        response = requests.delete(f"{url}{port}/users/{i+start_num}")
        # print("start_num",start_num+i)
        end_time = time.time()
        # Ensure successful response
        if response.status_code  in [200, 201, 204]:
            total_time += (end_time - start_time)
        else:
            print(f"{url}{port}/users/{i+start_num}")
            print(response.status_code)
            print(f"Failed request on port {port}")

    average_latency = total_time / num_requests
    return average_latency

def reset_database(url, port):
    response = requests.delete(f"{url}{port}/users/reset")
    if response.status_code == 200:
        print(f"Database reset on port {port}")
    else:
        print(f"Failed to reset database on port {port}")

def measure_complex_get_latency(url, port, endpoint, num_requests=50):
    total_tiome=0
    for i in range(num_requests):
        start_time = time.time()
        response = requests.get(f"{url}{port}{endpoint}")
        end_time = time.time()
        if response.status_code in [200, 201, 204]:
            total_tiome += (end_time - start_time)
        else:
            print(f"Failed request on port {port, endpoint, response.status_code, response.text}")
    average_latency = total_tiome / num_requests
    return average_latency

