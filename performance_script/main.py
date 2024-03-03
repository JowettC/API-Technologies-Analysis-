import requests
import time
from test_case1 import test_case_1
from test_case2 import test_case_2
from thoughput_test import throughput_test
from database_script.database_init import populate_data
import json

import importlib.util
import os

# Read JSON data into variables
# with open('./performance_script/config.json', 'r') as f:
with open('./config.json', 'r') as f:
    config = json.load(f)

ports = config['ports']
url = config['url']
labels = config['labels']
endpoints = config['endpoints']

# Example usage: print the variables
print("Ports:", ports)
print("URL:", url)
print("Labels:", labels)
print("Endpoints:", endpoints)



if __name__ == "__main__":
    # print(throughput_test(url, ports, labels))
    # Test Case 1
    populate_data(50)
    test_case_1_results = test_case_1(url, ports, labels)
    # Test Case 2
    populate_data(50)
    test_case_2_results_less_data = test_case_2(url, ports, labels, endpoints)

    populate_data(300)
    test_case_2_results_more_data = test_case_2(url, ports, labels, endpoints)

    # export the results into csv with labels as the header
    with open('results.csv', 'w') as f:
        f.write(f"{','.join(labels)}\n")
        for result in test_case_1_results:
            f.write(f"{','.join(map(str, result))}\n")
        f.write(f"{','.join(map(str, test_case_2_results_less_data))}\n")
        f.write(f"{','.join(map(str, test_case_2_results_more_data))}\n")



