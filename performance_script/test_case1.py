from util import measure_get_latency, measure_post_latency,measure_put_latency, measure_delete_latency

def get_request_comparison(url, ports, labels):
    latency_results = []
    for label, port in zip(labels, ports):
        avg_latency = measure_get_latency(url, port)
        if avg_latency is not None:
            latency_results.append((label, avg_latency))
    return latency_results

def post_request_comparison(url, ports, labels):
    latency_results = []
    for label, port in zip(labels, ports):
        avg_latency = measure_post_latency(url, port)
        if avg_latency is not None:
            latency_results.append((label, avg_latency))
    return latency_results

def put_request_comparison(url, ports, labels):
    latency_results = []
    for label, port in zip(labels, ports):
        avg_latency = measure_put_latency(url, port)
        if avg_latency is not None:
            latency_results.append((label, avg_latency))
    return latency_results

def delete_request_comparison(url, ports, labels):
    latency_results = []
    start_num = 51
    num_request = 5
    index = 0
    for label, port in zip(labels, ports):
        # print('index',index)
        if index != 0 and index % 3 == 0:
            start_num = 51
        avg_latency = measure_delete_latency(url, port,start_num, num_request)
        if avg_latency is not None:
            latency_results.append((label, avg_latency))
        start_num = start_num + num_request
        index = index + 1
    return latency_results


def test_case_1(url, ports, labels):
    print("=== Testing GET Request ===")
    print(get_request_comparison(url, ports, labels))
    print("=== Testing POST Request ===")
    print(post_request_comparison(url, ports, labels))
    print("=== Testing PUT Request ===")
    print(put_request_comparison(url, ports, labels))
    print("=== Testing DELETE Request ===")
    print(delete_request_comparison(url, ports, labels))