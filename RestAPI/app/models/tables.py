from app import app,db
from passlib.apps import custom_app_context as pwd_context
from datetime import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

class User(db.Model):
    __tablename__  = "users"

    id = db.Column(db.Integer,primary_key=True)

    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True,nullable=False)
    password = db.Column(db.String, nullable=False)

    def hash_password(self,password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self,password):
        return pwd_context.verify(password,self.password)

    def generate_auth_token(self, expiration=3600):
        # the token has an expiration time set to 3600
        # if the user logged time exceeds the expiration, the user have to
        # generate another token
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})
    @staticmethod
    def verify_auth_token(token):
        # check if the token is valid and returns user info if it is
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    @property
    def serialize(self):
        return {    'id': self.id,
                    'name': self.name,
                    'email': self.email
                }

    def __repr__(self):
        return "User %r>" % self.name

class Follow(db.Model):
    __tablename__ = "follow"

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    user = db.relationship('User', foreign_keys = user_id)
    follower = db.relationship('User', foreign_keys =follower_id)

    @property
    def serialize(self):
        return {
            'user': self.user.serialize,
            'follower': self.follower.serialize
        }

    def __repr__(self):
        return "<Follow %r>" % self.id

class Post(db.Model):
        __tablename__ = "posts"

        id = db.Column(db.Integer,primary_key=True)
        content = db.Column(db.Text,nullable=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        h_post = db.Column(db.DateTime,default=datetime.now())

        user = db.relationship('User', foreign_keys = user_id)

        @property
        def serialize(self):
            return {
                'user': self.user.serialize,
                'content': self.content,
                'time': self.h_post.strftime("%w %b %y -- %H:%M")
            }

        def __repr__(self):
            return "<Post %r>" %self.id
