from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
from datetime import datetime
import random

app = FastAPI()
uri = "bolt://neo4j:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "yourStrongPasswordHere"))

def get_session():
    return driver.session()

@app.get("/")
def hello():
    return "Hello, World!"

@app.get("/users")
def read_users():
    with get_session() as session:
        result = session.run("MATCH (u:User) RETURN u.username AS username, u.email AS email, u.user_id AS user_id")
        return [record.data() for record in result]

@app.post("/users")
def create_user(data: dict):
    with get_session() as session:
        result = session.run("MATCH (u:User) RETURN max(u.user_id) AS max_user_id")
        max_user_id = result.single()["max_user_id"]
        user_id = max_user_id + 1 if max_user_id else 1
        result = session.run("CREATE (u:User {username: $username, email: $email, user_id: $user_id}) RETURN u.user_id AS user_id", username=data['username'], email=data['email'], user_id=user_id)
        user_id = result.single()["user_id"]
        return {'username': data['username'], 'email': data['email'], 'user_id': user_id}

@app.put("/users/{user_id}")
def update_user(user_id: int, data: dict):
    with get_session() as session:
        result = session.run("MATCH (u:User {user_id: $user_id}) SET u.username = $username, u.email = $email RETURN u.user_id AS user_id", user_id=user_id, username=data['username'], email=data['email'])
        if not result.single():
            raise HTTPException(status_code=404, detail="User not found")
        return {'username': data['username'], 'email': data['email'], 'user_id': user_id}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with get_session() as session:
        result = session.run("MATCH (u:User {user_id: $user_id}) DELETE u RETURN count(u) AS count", user_id=user_id)
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {'message': 'User deleted'}

@app.get("/users/posts")
def read_user_posts():
    with get_session() as session:
        result = session.run("""
            MATCH (u:User)-[:POSTED]->(p:Post)
            RETURN p.content AS content, u.email AS email, u.user_id AS user_id, u.username AS username
        """)
        return [record.data() for record in result]

@app.get("/users/comments")
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
        return final_result


@app.get("/comments/")
async def get_comments():
    with driver.session() as session:
        result = session.read_transaction(get_all_comments_tx)
    return result

def get_all_comments_tx(tx):
    result = tx.run("""
            MATCH (u:User)-[c:COMMENTED]->(p:Post)
            RETURN u.username AS username, p.content AS post_content, c.comment_text AS comment_text, c.timestamp AS timestamp
            """)
    return [record.data() for record in result]

@app.get("/posts/likes")
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
        return final_result

@app.get("/posts/likes/users")
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
        return final_result

# uvicorn graph_fast_api_app:app --reload --port 8020