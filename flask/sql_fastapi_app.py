from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from marshmallow import Schema, fields, ValidationError

# Flask Application Setup
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:example@localhost/socialmedia"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ORM model for the Users table
class UserModel(db.Model):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

# Schema for User Data Validation
class UserSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# CREATE
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_user = UserModel(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return user_schema.dump(new_user), 201

# READ
@app.route('/users', methods=['GET'])
def read_users():
    users = UserModel.query.all()
    return jsonify(users_schema.dump(users)), 200

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
    return user_schema.dump(user), 200

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

# Run the Flask app
if __name__ == '__main__':
    db.create_all()  # Create database tables
    app.run(debug=True)
