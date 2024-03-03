from util import measure_complex_get_latency

def test_case_2(url, ports, labels, endpoints):
    res = []
    for label, port in zip(labels, ports):
        endpoint_sum = 0
        for endpoint in endpoints:
            avg_latency = measure_complex_get_latency(url, port, endpoint)
            if avg_latency is not None:
                print(f"Average latency for {label} on {endpoint}: {avg_latency:.5f} seconds")
                endpoint_sum += avg_latency
            else:
                raise Exception(f"Failed to measure latency for {label} on {endpoint}")
        res.append(endpoint_sum / len(endpoints))
    return res

