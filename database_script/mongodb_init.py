from pymongo import MongoClient
import random
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["socialmedia"]
users = db["users"]

# Insert dummy data
for i in range(1, 51):
    user = {
        "user_id": i,
        "username": f"user{i}",
        "email": f"user{i}@example.com",
        "posts": [{
            "content": f"Post content {i}",
            "timestamp": datetime.now(),
            "comments": [{"user_id": random.randint(1, 50), "comment_text": f"Comment text {i}", "timestamp": datetime.now()} for _ in range(5)],
            "likes": [{"user_id": random.randint(1, 50), "timestamp": datetime.now()} for _ in range(5)]
        }]
    }
    users.insert_one(user)

# erase all data
# users.delete_many({})
# print("Data erased")
