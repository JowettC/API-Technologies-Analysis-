from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from marshmallow import Schema, fields, ValidationError
from sqlalchemy.orm import joinedload

# Flask Application Setup
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:example@localhost/socialmedia"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ORM model for the Users table
class UserModel(db.Model):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

# ORM model for posts table
class PostModel(db.Model):
    __tablename__ = "posts"
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500), nullable=False)
    user_id = Column(Integer, db.ForeignKey('users.user_id'), nullable=False)
    comments = db.relationship('CommentModel', backref='post', lazy=True)
    user = db.relationship('UserModel', backref='posts', lazy=True)
    likes = db.relationship('LikeModel', backref='post', lazy=True)
    def __repr__(self):
        return f"Post('{self.content}')"

class CommentModel(db.Model):
    __tablename__ = "comments"
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_id = Column(Integer, db.ForeignKey('users.user_id'), nullable=False)
    comment_text = Column(String(500), nullable=False)
    user = db.relationship('UserModel', backref='comments', lazy=True)

class LikeModel(db.Model):
    __tablename__ = "likes"
    like_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_id = Column(Integer, db.ForeignKey('users.user_id'), nullable=False)
    user = db.relationship('UserModel', backref='likes', lazy=True)

# Schema for User Data Validation
class UserSchema(Schema):
    user_id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)

# Schema for Post Data Validation
class PostSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)

# Schema for Comment Data Validation
class CommentSchema(Schema):
    comment_text = fields.Str(required=True)

# Schema for Like Data Validation
class LikeSchema(Schema):
    like_id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    post_id = fields.Int(required=True)

class LikeUserSchema(Schema):
    user = fields.Nested(UserSchema)

# Schema instances
post_schema = PostSchema()
posts_schema = PostSchema(many=True)

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

like_schema = LikeSchema()
likes_schema = LikeSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

like_user_schema = LikeUserSchema(many=True)

# READ
@app.route('/users', methods=['GET'])
def read_users():
    users = UserModel.query.all()
    return jsonify(users_schema.dump(users)), 200

# create a new user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_user = UserModel(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user_schema.dump(new_user)), 201

# UPDATE
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = UserModel.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404

    try:
        data = user_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user.username = data['username']
    user.email = data['email']
    db.session.commit()
    return jsonify(user_schema.dump(user)), 200

# DELETE
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = UserModel.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

@app.route('/')
def read_root():
    return {"Application details": "Flask SQL application"}

# complex query to get the user and their posts 
@app.route('/users/posts', methods=['GET'])
def read_user_posts():
    posts = PostModel.query.options(db.joinedload(PostModel.user)).all()
    result = []
    for post in posts:
        post_data = post_schema.dump(post)
        post_data['user'] = user_schema.dump(post.user)
        result.append(post_data)
    return result, 200
    

# compelex query to get the user and their comments and the post they commented on
@app.route('/users/comments', methods=['GET'])
def read_user_comments():
    users = UserModel.query.options(db.joinedload(UserModel.comments)).all()
    result = []
    for user in users:
        user_data = user_schema.dump(user)
        user_data['comments'] = comments_schema.dump(user.comments)
        result.append(user_data)
    return result, 200

# complex query to number of likes per posts
@app.route('/posts/likes', methods=['GET'])
def read_post_likes():
    posts = PostModel.query.options(db.joinedload(PostModel.likes)).all()
    result = []
    for post in posts:
        post_data = post_schema.dump(post)
        post_data['likes'] = likes_schema.dump(post.likes)
        result.append(post_data)
    return result, 200

# which users like which post
@app.route('/posts/likes/users', methods=['GET'])
def read_post_likes_users():
    posts = PostModel.query.options(db.joinedload(PostModel.likes).joinedload(LikeModel.user)).all()
    result = []
    # use like user schema to include user details
    for post in posts:
        post_data = post_schema.dump(post)
        post_data['likes'] = like_user_schema.dump(post.likes)
        result.append(post_data)

    return result, 200



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=8001, host='0.0.0.0')
