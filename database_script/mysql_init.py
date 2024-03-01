import pymysql
import pymysql.cursors
import random
from datetime import datetime

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='example',
                             database='socialmedia',
                             cursorclass=pymysql.cursors.DictCursor)
def insertDataIntoMySQL():
    print("=== Starting Script to insert data into MySQL ===")
    with connection:
        with connection.cursor() as cursor:
             # delete all tables before inserting new data
            cursor.execute("DROP TABLE IF EXISTS comments")
            cursor.execute("DROP TABLE IF EXISTS likes")
            cursor.execute("DROP TABLE IF EXISTS posts")
            cursor.execute("DROP TABLE IF EXISTS users")
            connection.commit()
            print("Data erased before inserting new data")
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50),
                    email VARCHAR(100)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    post_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    content TEXT,
                    timestamp DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    comment_id INT AUTO_INCREMENT PRIMARY KEY,
                    post_id INT,
                    user_id INT,
                    comment_text TEXT,
                    timestamp DATETIME,
                    FOREIGN KEY (post_id) REFERENCES posts(post_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS likes (
                    like_id INT AUTO_INCREMENT PRIMARY KEY,
                    post_id INT,
                    user_id INT,
                    timestamp DATETIME,
                    FOREIGN KEY (post_id) REFERENCES posts(post_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            """)

            # Insert dummy data
            for i in range(1, 51):
                cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (f'user{i}', f'user{i}@example.com'))
            connection.commit()

            for i in range(1, 51):
                cursor.execute("INSERT INTO posts (user_id, content, timestamp) VALUES (%s, %s, %s)", (random.randint(1, 50), f'Post content {i}', datetime.now()))
            connection.commit()

            for i in range(1, 51):
                cursor.execute("INSERT INTO comments (post_id, user_id, comment_text, timestamp) VALUES (%s, %s, %s, %s)", (random.randint(1, 50), random.randint(1, 50), f'Comment text {i}', datetime.now()))
            connection.commit()

            for i in range(1, 51):
                cursor.execute("INSERT INTO likes (post_id, user_id, timestamp) VALUES (%s, %s, %s)", (random.randint(1, 50), random.randint(1, 50), datetime.now()))
            connection.commit()
            print("=== Finish inserting data to MySQL ===")
