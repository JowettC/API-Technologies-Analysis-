from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from datetime import datetime
import random

app = Flask(__name__)
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "yourStrongPasswordHere"))

def get_session():
    return driver.session()

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/users", methods=["GET"])
def read_users():
    with get_session() as session:
        result = session.run("MATCH (u:User) RETURN u.username AS username, u.email AS email, u.user_id AS user_id")
        return jsonify([record.data() for record in result])

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    with get_session() as session:
        result = session.run("MATCH (u:User) RETURN max(u.user_id) AS max_user_id")
        max_user_id = result.single()["max_user_id"]
        user_id = max_user_id + 1 if max_user_id else 1
        result = session.run("CREATE (u:User {username: $username, email: $email, user_id: $user_id}) RETURN u.user_id AS user_id", username=data['username'], email=data['email'], user_id=user_id)
        user_id = result.single()["user_id"]
        return jsonify({'username': data['username'], 'email': data['email'], 'user_id': user_id})

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    with get_session() as session:
        result = session.run("MATCH (u:User {user_id: $user_id}) SET u.username = $username, u.email = $email RETURN u.user_id AS user_id", user_id=user_id, username=data['username'], email=data['email'])
        if not result.single():
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'username': data['username'], 'email': data['email'], 'user_id': user_id})

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    with get_session() as session:
        result = session.run("MATCH (u:User {user_id: $user_id}) DELETE u RETURN count(u) AS count", user_id=user_id)
        if result.single()["count"] == 0:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'message': 'User deleted'})

@app.route("/users/posts", methods=["GET"])
def read_user_posts():
    with get_session() as session:
        result = session.run("""
            MATCH (u:User)-[:POSTED]->(p:Post)
            RETURN p.content AS content, u.email AS email, u.user_id AS user_id, u.username AS username
        """)
        return jsonify([record.data() for record in result])

@app.route("/users/comments", methods=["GET"])
def read_user_comments():
    with get_session() as session:
        result = session.run("""
            MATCH (u:User)-[c:COMMENTED]->(p:Post)
            RETURN u.email AS email, u.user_id AS user_id, u.username AS username, c.comment_text AS comment_text
        """)
        comments_user_id_mapping = {}
        for record in result:
            user_id = record["user_id"]
            comment_text = record["comment_text"]
            if user_id not in comments_user_id_mapping:
                comments_user_id_mapping[user_id] = []
            comments_user_id_mapping[user_id].append({'comment_text': comment_text})
        final_result = []
        for user_id, comments in comments_user_id_mapping.items():
            final_result.append({'user': {'email': record["email"], 'user_id': user_id, 'username': record["username"]}, 'comments': comments})
        return jsonify(final_result)

@app.route("/comments/", methods=["GET"])
def get_comments():
    with driver.session() as session:
        result = session.read_transaction(get_all_comments_tx)
    return jsonify(result)

def get_all_comments_tx(tx):
    result = tx.run("""
            MATCH (u:User)-[c:COMMENTED]->(p:Post)
            RETURN u.username AS username, p.content AS post_content, c.comment_text AS comment_text, c.timestamp AS timestamp
            """)
    return [record.data() for record in result]

@app.route("/posts/likes", methods=["GET"])
def read_post_likes():
    with get_session() as session:
        result = session.run("""
            MATCH (u:User)-[:POSTED]->(p:Post)<-[:LIKED]-(l:User)
            RETURN p.content AS content, l.user_id AS user_id
        """)
        likes_post_id_mapping = {}
        for record in result:
            content = record["content"]
            user_id = record["user_id"]
            if content not in likes_post_id_mapping:
                likes_post_id_mapping[content] = []
            likes_post_id_mapping[content].append({'user_id': user_id})
        final_result = []
        for post, likes in likes_post_id_mapping.items():
            final_result.append({'post': post, 'likes': likes})
        return jsonify(final_result)

@app.route("/posts/likes/users", methods=["GET"])
def read_post_likes_users():
    with get_session() as session:
        result = session.run("""
            MATCH (u:User)-[:POSTED]->(p:Post)<-[:LIKED]-(l:User)
            RETURN p.content AS content, l.user_id AS user_id, l.username AS username, l.email AS email
        """)
        likes_post_id_mapping = {}
        for record in result:
            content = record["content"]
            user_id = record["user_id"]
            username = record["username"]
            email = record["email"]
            if content not in likes_post_id_mapping:
                likes_post_id_mapping[content] = []
            likes_post_id_mapping[content].append({'user_id': user_id, 'username': username, 'email': email})
        final_result = []
        for post, likes in likes_post_id_mapping.items():
            final_result.append({'post': post, 'likes': likes})
        return jsonify(final_result)

if __name__ == "__main__":
    app.run(port=8021)