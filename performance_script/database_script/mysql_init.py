import pymysql
import pymysql.cursors
import random
from datetime import datetime

# Function to insert data into MySQL
def insert_data_into_mysql(data=50):
    print("=== Starting Script to Insert Data into MySQL ===")
    try:
        # Connect to the database
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='example',
                                     database='socialmedia',
                                     cursorclass=pymysql.cursors.DictCursor)
        
        cursor = connection.cursor()

        # Delete all tables before inserting new data
        cursor.execute("DROP TABLE IF EXISTS comments")
        cursor.execute("DROP TABLE IF EXISTS likes")
        cursor.execute("DROP TABLE IF EXISTS posts")
        cursor.execute("DROP TABLE IF EXISTS users")
        
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

        connection.commit()

        # Insert dummy data
        for i in range(1, data + 1):
            cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (f'user{i}', f'user{i}@example.com'))
        connection.commit()

        for i in range(1, data + 1):
            cursor.execute("INSERT INTO posts (user_id, content, timestamp) VALUES (%s, %s, %s)", 
                           (random.randint(1, 50), f'Post content {i}', datetime.now()))
        connection.commit()

        for i in range(1, data + 1):
            cursor.execute("INSERT INTO comments (post_id, user_id, comment_text, timestamp) VALUES (%s, %s, %s, %s)", 
                           (random.randint(1, 50), random.randint(1, 50), f'Comment text {i}', datetime.now()))
        connection.commit()

        for i in range(1, data + 1):
            cursor.execute("INSERT INTO likes (post_id, user_id, timestamp) VALUES (%s, %s, %s)", 
                           (random.randint(1, 50), random.randint(1, 50), datetime.now()))
        connection.commit()

        print("=== Finished Inserting Data to MySQL ===")

    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

# Example usage
if __name__ == "__main__":
    insert_data_into_mysql(300)
