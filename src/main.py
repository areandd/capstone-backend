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
from mailer import Mailer
import random
import smtplib
from email.message import EmailMessage
#from models import Person

app = Flask(__name__)
# reset_code
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
            user_name = requestBody["user_name"]
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
    user = User.query.get(token)
    return jsonify(loggedInAs = token, user_name = user.user_name), 200

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
    id = get_jwt_identity()
    watchList = Watchlist.query.filter_by(user_id=id)
    fullWatchlist = list(map(lambda stock: stock.serialize(), watchList))
    return jsonify(fullWatchlist)

@app.route('/watchlist-add', methods=['POST'])
@jwt_required()
def addToWatchlist():
    requestBody = request.get_json(force=True)
    user_id = requestBody['user_id']
    stock = requestBody['stock']
    watchlist = Watchlist(
        user_id = user_id,
        stock = stock
    )
    db.session.add(watchlist)
    db.session.commit()
    return jsonify('Success'), 200


@app.route('/watchlist-delete', methods=['DELETE'])
@jwt_required()
def deleteFromWatchlist():
    requestBody = request.get_json(force=True)
    user_id = requestBody['user_id']
    stock = requestBody['stock']
    find_stock = Watchlist.query.filter_by(user_id = user_id, stock = stock).first()
    if(find_stock):
        db.session.delete(find_stock)
        db.session.commit()
        return jsonify('Stock deletion successful'), 200
    else:
        return jsonify('Unsuccessful'), 400
    # requestBody = request.get_json(force=True)
    # user_id = requestBody['user_id']
    # stock = requestBody['stock']
    # find_stock = User.query.filter_by(user_id = user_id, stock = stock).first()
    # if(find_stock and stock = stock):


    

# posts = Posts.query.all()
#     allPosts = list(map(lambda post: post.serialize(), posts))
#     return jsonify(allPosts)



@app.route('/reset-password', methods=['POST'])
def reset_password():
    global email_code 
    requestBody = request.get_json(force=True)
    email = requestBody['email']
    reset_code = random.randint(1000, 99000)
    check_email = User.query.filter_by(email = email).first()
    admin_email = "goodstocksreset@gmail.com"
    admin_password = "aimkhkmrsdiogksp"
    if (check_email):
        message = EmailMessage()
        message["Subject"] = "reset your password"
        message["From"] = admin_email
        message["To"] = email
        message.set_content("reset code: " + str(reset_code))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp: 
            smtp.login(admin_email, admin_password)
            smtp.send_message(message)
        email_code = reset_code
        return jsonify("successfully sent email to reset"), 200
    else:
        return jsonify("you failed to send reset email"), 400

@app.route('/verify-code', methods=['POST'])
def verify_code():
    requestBody = request.get_json(force=True)
    code = requestBody['password_code']
    print(email_code)
    if (int(code) == email_code):
        return jsonify('code verified'), 200
    else:
        return jsonify('did not work'), 400

@app.route('/change-password', methods=['PUT'])
def change_password():
    requestBody = request.get_json(force=True)
    code = requestBody['password_code']
    email = requestBody['email']
    new_password = hashlib.sha224(requestBody['password'].encode("UTF-8")).hexdigest()
    find_user = User.query.filter_by(email = email).first()
    if (find_user and int(code) == email_code):
        find_user.password = new_password
        db.session.commit()
        return jsonify('Password successfully changed'), 200
    else:
        return jsonify('Unsuccessful, try again'), 400

    
@app.route("/profile-changes", methods=["PUT"])
@jwt_required()
def modify_profile():
    requestBody = request.get_json(force=True)
    user = User.query.get(requestBody["userId"])
    name = requestBody["name"]
    user_name = requestBody["user_name"]
    bio = requestBody["bio"]
    if name:
        user.name = name
    if user_name:
        user.user_name = user_name
    if bio:
        user.bio = bio
    db.session.commit()
    return jsonify("success"), 200


@app.route("/user-profile", methods=["GET"])
def check_user():
    
    user_name = request.args.get("key")
    if user_name:
        user = User.query.filter_by(user_name = user_name).first()
        user_info = user.serialize()
        print(user)
        if user:
            return jsonify(user_info), 200
        else:
            return jsonify("user does not exist!"), 400
     
        

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
