import os
import datetime
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from dotenv import load_dotenv
from models import db, Role, User
from werkzeug.security import generate_password_hash, check_password_hash
from math import ceil

load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('DEBUG', False) 
app.config['ENV'] = os.getenv('ENV', 'production') 
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI') 
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)
Migrate(app, db)
CORS(app)
jwt = JWTManager(app)

@app.route('/')
def main():
    return jsonify({ "msg": "API REST Flask" }), 200

@app.route('/api/auth/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    user = User.query.filter_by(email=email).first()

    if not user: return jsonify({ "error":"Username/Password son incorrectos" }), 401
    if not check_password_hash(user.password, password): return jsonify({ "error":"Username/Password son incorrectos" }), 401

    expires = datetime.timedelta(days=3)
    access_token = create_access_token(identity=user.id, expires_delta=expires)

    data = {
        "access_token": access_token,
        "user": user.serialize_with_roles()
    }
    
    return jsonify(data), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')
    

    user = User()
    user.name = name
    user.email = email 
    user.password = generate_password_hash(password)

    role = Role.query.filter_by(name="Client").first()
    user.roles.append(role)

    user.save()

    if user:
        expires = datetime.timedelta(days=3)
        access_token = create_access_token(identity=user.id, expires_delta=expires)

        data = {
            "access_token": access_token,
            "user": user.serialize_with_roles()
        }

        return jsonify(data), 200

    return jsonify({ "Error": "Por favor intente mas tarde" }), 400

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))


    #users = User.query.all()
    #users = list(map(lambda user: user.serialize_with_roles(), users))

    users = User.query.paginate(page=page, per_page=per_page, max_per_page=10)
    data = {
        "page": users.page,
        "results": list(map(lambda user: user.serialize_with_roles(), users.items)),
        "per_page": users.per_page,
        "pages": users.pages,
        "total": users.total,
        "next": users.next_num,
        "prev": users.prev_num,
    }

    return jsonify(data), 200


@app.route('/api/users', methods=['POST'])
@jwt_required()
def create_user():

    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')
    roles = request.json.get('roles') #  [1, 2]

    user = User()
    user.name = name
    user.email = email 
    user.password = generate_password_hash(password)

    for role_id in roles:
        role = Role.query.get(role_id)
        if role and not role in user.roles: user.roles.append(role)

    user.save()

    return jsonify(user.serialize()), 201


@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():

    id = get_jwt_identity()
    user = User.query.get(id)

    return jsonify({ "private path": "private info app", "user": user.serialize_with_roles()}), 200


if __name__ == '__main__':
    app.run()