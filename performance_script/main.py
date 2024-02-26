import requests
import time
from util import measure_get_latency

ports = ['8000', '8001', '8002', '8010', '8011', '8012', '8020', '8021', '8022']
url = "http://localhost:"
labels = [
    "FastAPI with SQL",
    "FastAPI with NoSQL",
    "FastAPI with Graph",
    "Flask with SQL",
    "Flask with NoSQL",
    "Flask with Graph",
    "Express with SQL",
    "Express with NoSQL",
    "Express with Graph"
]

endpoints = [
    "/users"
    "/users/posts",
    "/users/comments",
    "/posts/likes",
    "/posts/likes/users",
]


# Test case 1: CRUD operations (GET, POST, PUT, DELETE) measure latency and throughput
test_case_1_endpoint = "/users"
# Get request
# Array to store results
latency_results = []

# Measure GET request latency for each application and store results
for label, port in zip(labels, ports):
    avg_latency = measure_get_latency(url, port)
    if avg_latency is not None:
        latency_results.append((label, avg_latency))

# Print results
for label, latency in latency_results:
    print(f"{label}: Average GET request latency = {latency:.4f} seconds")





