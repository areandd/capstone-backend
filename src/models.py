from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(25), unique=False, nullable=False, default="name")
    user_name = db.Column(db.String(25), unique=True, nullable=False)
    banner = db.Column(db.String(500), default="https://pbs.twimg.com/media/D-jnKUPU4AE3hVR.jpg", unique=False)
    profile_photo = db.Column(db.String(500), default="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png", unique=False)
    bio = db.Column(db.String(250), unique=False)
    following = db.Column(db.Integer, unique=False)
    followers = db.Column(db.Integer, unique=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    watchlist = db.relationship('Watchlist')
    posts = db.relationship('Posts')

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "banner": self.banner,
            "name": self.name,
            "user_name": self.user_name,
            "profile_photo": self.profile_photo,
            "bio": self.bio,
            "following": self.following,
            "followers": self.followers,
            # do not serialize the password, its a security breach
        }

class Posts(db.Model):
    __tablename__ = 'Posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    headline = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(240), nullable=False)
    date_stamp = db.Column(db.String(80), nullable=False)

    user = db.relationship('User', foreign_keys = [user_id])

    def __repr__(self):
        return '<Posts %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "headline": self.headline,
            "content": self.content,
            "date_stamp": self.date_stamp
            # do not serialize the password, its a security breach
        }

class Watchlist(db.Model):
    __tablename__ = 'Watchlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    stock = db.Column(db.String(10), unique=False, nullable=False)

    user = db.relationship('User', foreign_keys = [user_id])

    def __repr__(self):
        return '<Watchlist %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "stock": self.stock
            # do not serialize the password, its a security breach
        }