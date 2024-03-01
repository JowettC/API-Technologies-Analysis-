import requests
import time
from test_case1 import test_case_1

import json

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
    # Test Case 1
    test_case_1(url, ports, labels)


