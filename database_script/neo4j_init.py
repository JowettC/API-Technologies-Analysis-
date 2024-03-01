from neo4j import GraphDatabase
from datetime import datetime
import random
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "yourStrongPasswordHere"))

def insertDataIntoNeo4j():
    print("=== Starting Script to insert data into Neo4j ===")
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("Data erased before inserting new data")
    def add_dummy_data(tx):
        for i in range(1, 51):
            tx.run("CREATE (u:User {username: $username, email: $email, user_id: $user_id})", username=f"user{i}", email=f"user{i}@example.com", user_id=i)
            tx.run("""
                MATCH (u:User {username: $username})
                CREATE (u)-[:POSTED]->(p:Post {content: $content, timestamp: $timestamp})
                """, username=f"user{i}", content=f"Post content {i}", timestamp=datetime.now().isoformat())
            tx.run("""
                MATCH (u:User {username: $username}), (p:Post {content: $content})
                CREATE (u)-[:COMMENTED {comment_text: $comment_text, timestamp: $timestamp}]->(p)
                """, username=f"user{random.randint(1, 50)}", content=f"Post content {random.randint(1, 50)}", comment_text=f"Comment text {i}", timestamp=datetime.now().isoformat())
            tx.run("""
                MATCH (u:User {username: $username}), (p:Post {content: $content})
                CREATE (u)-[:LIKED {timestamp: $timestamp}]->(p)
                """, username=f"user{random.randint(1, 50)}", content=f"Post content {random.randint(1, 50)}", timestamp=datetime.now().isoformat())

    with driver.session() as session:
        session.execute_write(add_dummy_data)
    print("=== Finish inserting data to Neo4j ===")


driver.close()

