"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Posts, Watchlist
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import hashlib
#from models import Person

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)

app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

@app.route('/signup', methods=['POST'])
def handle_signup():
    requestBody = request.get_json(force=True)
    checkEmail = bool(User.query.filter_by(email = requestBody['email']).first())
    if checkEmail:
        return jsonify('Email exists already')
    else:
        email = requestBody['email']
        hash_password = hashlib.sha224(requestBody['password'].encode("UTF-8")).hexdigest()
        user = User(
            email = email,
            password = hash_password,
        )
        db.session.add(user)
        db.session.commit()
        return jsonify('Success'), 200

@app.route('/login', methods=['POST'])
def handle_login():
    requestBody = request.get_json(force=True)
    email = requestBody['email']
    hash_password = hashlib.sha224(requestBody['password'].encode("UTF-8")).hexdigest()
    checkUser = User.query.filter_by(email = email, password = hash_password).first()
    if checkUser:
        user_token = create_access_token(identity = checkUser.id)
        return jsonify(user_token), 200
    else:
        return jsonify('User does not exist'), 401

@app.route('/validate-token', methods=['GET'])
@jwt_required()
def handle_token():
    token = get_jwt_identity()
    return jsonify(loggedInAs = token), 200

@app.route('/posts', methods=['GET'])
@jwt_required()
def handle_getPosts():
    posts = Posts.query.all()
    allPosts = list(map(lambda post: post.serialize(), posts))
    return jsonify(allPosts)

@app.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    requestBody = request.get_json(force=True)
    user_id = requestBody['user_id']
    headline = requestBody['headline']
    content = requestBody['content']
    date_stamp = requestBody['date_stamp']
    post = Posts(
        user_id = user_id,
        headline = headline,
        content = content,
        date_stamp = date_stamp
    )
    db.session.add(post)
    db.session.commit()
    return jsonify('Success'), 200


@app.route('/watchlist', methods=['GET'])
@jwt_required()
def handle_watchlist():
    requestBody = request.get_json(force=True)
    userId = requestBody['user_id']
    watchList = Watchlist.query.filter_by(user_id = userId).all()
    fullWatchlist = list(map(lambda stock: stock.serialize(), watchList))
    return jsonify(fullWatchlist)














# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
