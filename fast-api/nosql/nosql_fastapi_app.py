from fastapi import FastAPI
from fastapi import HTTPException
from pymongo import MongoClient

app = FastAPI()
client = MongoClient("mongodb://mongo:27017/")
db = client["socialmedia"]
users_collection = db["users"]

@app.get("/")
def hello():
    return "Hello, World!"

@app.get("/users")
def read_users():
    users = users_collection.find()
    result = []
    for user in users:
        result.append({'username': user['username'], 'email': user['email'], 'user_id': user['user_id']})
    return result


@app.post("/users")
def create_user(data: dict):
    last_user = users_collection.find().sort('user_id', -1).limit(1)
    user_id = 1
    if last_user:
        user_id = last_user[0]['user_id'] + 1
    user = {'username': data['username'], 'email': data['email'], 'user_id': user_id, 'posts': []}
    users_collection.insert_one(user)
    return {'username': data['username'], 'email': data['email'], 'user_id': user_id}

@app.put("/users/{user_id}")
def update_user(user_id: int, data: dict):
    user = users_collection.find_one({'user_id': user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    users_collection.update_one({'user_id': user_id}, {'$set': {'username': data['username'], 'email': data['email']}})
    return {'username': data['username'], 'email': data['email'], 'user_id': user_id}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    user = users_collection.find_one({'user_id': user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    users_collection.delete_one({'user_id': user_id})
    return {'message': 'User deleted'}

@app.get("/users/posts")
def read_user_posts():
    users = users_collection.find()
    result = []
    for user in users:
        posts = user['posts']
        for post in posts:
            post_with_user = {
                "content": post["content"],
                "user": {
                    "email": user["email"],
                    "user_id": user["user_id"],
                    "username": user["username"]
                }
            }
            result.append(post_with_user)
    return result

@app.get("/users/comments")
def read_user_comments():
    users = users_collection.find()
    comments_user_id_mapping = {}

    for user in users:
        comments = user['posts']
        for comment in comments:
            for c in comment['comments']:
                if c['user_id'] not in comments_user_id_mapping:
                    comments_user_id_mapping[c['user_id']] = []
                comments_user_id_mapping[c['user_id']].append({'comment_text': c["comment_text"]})
    result = []
    for user_id, comments in comments_user_id_mapping.items():
        user = users_collection.find_one({'user_id': user_id})
        result.append({'user': {'email': user["email"], 'user_id': user["user_id"], 'username': user["username"]}, 'comments': comments})
    return result

@app.get("/posts/likes")
def read_post_likes():
    users = users_collection.find()
    likes_post_id_mapping = {}

    for user in users:
        posts = user['posts']
        for post in posts:
            for like in post['likes']:
                if post['content'] not in likes_post_id_mapping:
                    likes_post_id_mapping[post['content']] = []
                likes_post_id_mapping[post['content']].append({'user_id': like["user_id"]})
    result = []
    for post, likes in likes_post_id_mapping.items():
        result.append({'post': post, 'likes': likes})
    return result

@app.get("/posts/likes/users")
def read_post_likes_users():
    users = users_collection.find()
    likes_post_id_mapping = {}

    for user in users:
        posts = user['posts']
        for post in posts:
            for like in post['likes']:
                if post['content'] not in likes_post_id_mapping:
                    likes_post_id_mapping[post['content']] = []
                user = users_collection.find_one({'user_id': like["user_id"]})
                likes_post_id_mapping[post['content']].append({'user_id': like["user_id"], 'username': user["username"], 'email': user["email"]})
    result = []
    for post, likes in likes_post_id_mapping.items():
        result.append({'post': post, 'likes': likes})
    return result

# uvicorn nosql_fastapi_app:app --reload --port 8010