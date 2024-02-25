from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/socialmedia"
mongo = PyMongo(app)

@app.route('/')
def hello():
    return 'Hello, World!'

# get all users
@app.route('/users', methods=['GET'])
def read_users():
    users = mongo.db.users.find()
    result = []
    for user in users:
        result.append({'username': user['username'], 'email': user['email'], 'user_id': user['user_id']})
    return jsonify(result), 200

# egt eevrything from 1 user
@app.route('/users/<user_id>', methods=['GET'])
def read_user(user_id):
    user_id = int(user_id)
    user = mongo.db.users.find_one({'user_id': user_id})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'username': user['username'], 'email': user['email'], 'user_id': user['user_id'], 'posts': user["posts"]}), 200

#  create user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    # get last user_id
    last_user = mongo.db.users.find().sort('user_id', -1).limit(1)
    user_id = 1
    if last_user:
        user_id = last_user[0]['user_id'] + 1
    # create user
    mongo.db.users.insert_one({'username': data['username'], 'email': data['email'], 'user_id': user_id, 'posts': []})
    # return user
    return jsonify({'username': data['username'], 'email': data['email'], 'user_id': user_id}), 201

# update user
@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    user_id = int(user_id)
    user = mongo.db.users.find_one({'user_id': user_id})
    print(user, "terst")
    if not user:
        return jsonify({'message': 'User not found'}), 404
    mongo.db.users.update_one({'user_id': user_id}, {'$set': {'username': data['username'], 'email': data['email']}})
    print(mongo.db.users.find_one({'user_id': user_id}))
    return jsonify({'username': data['username'], 'email': data['email'], 'user_id': user_id}), 201

# delete user
@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user_id = int(user_id)
    user = mongo.db.users.find_one({'user_id': user_id})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    mongo.db.users.delete_one({'user_id': user_id})
    return jsonify({'message': 'User deleted'}), 200

# complex query to get the user and their posts 
@app.route('/users/posts', methods=['GET'])
def read_user_posts():
    users = mongo.db.users.find()
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
    return jsonify(result), 200


# compelex query to get the user and their comments and the post they commented on
@app.route('/users/comments', methods=['GET'])
def read_user_comments():
    users = mongo.db.users.find()
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
        user = mongo.db.users.find_one({'user_id': user_id})
        result.append({'user': {'email': user["email"], 'user_id': user["user_id"], 'username': user["username"]}, 'comments': comments})
    return jsonify(result), 200


# which users like which post
@app.route('/posts/likes', methods=['GET'])
def read_post_likes():
    users = mongo.db.users.find()
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
    return jsonify(result), 200

# which users like which post
@app.route('/posts/likes/users', methods=['GET'])
def read_post_likes_users():
    users = mongo.db.users.find()
    likes_post_id_mapping = {}

    for user in users:
        posts = user['posts']
        for post in posts:
            for like in post['likes']:
                if post['content'] not in likes_post_id_mapping:
                    likes_post_id_mapping[post['content']] = []
                user = mongo.db.users.find_one({'user_id': like["user_id"]})
                likes_post_id_mapping[post['content']].append({'user_id': like["user_id"], 'username': user["username"], 'email': user["email"]})
    result = []
    for post, likes in likes_post_id_mapping.items():
        result.append({'post': post, 'likes': likes})
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(port=8011, host='0.0.0.0')