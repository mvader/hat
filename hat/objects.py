from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flaskext.bcrypt import generate_password_hash, check_password_hash

from datetime import datetime

db = SQLAlchemy()
session = db.session

login_manager = LoginManager()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    pwdhash = db.Column(db.String(100))

    def __init__(self, **kw):
        for k in kw:
            setattr(self, k, kw.get(k))

    @classmethod
    def register(cls, email, password):
        if session.query(cls.query.filter_by(email=email).exists()).scalar():
            return None

        pwdhash = generate_password_hash(password)
        u = cls(email=email, pwdhash=pwdhash)

        session.add(u)
        session.commit()

        return u

    @classmethod
    def login(cls, email, password):
        u = cls.query.filter_by(email=email).first()
        if u is None:
            return None
       
        if check_password_hash(u.pwdhash, password):
            return u
        return None

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_id(self):
        return unicode(self.id)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Text)
    link = db.Column(db.Text)
    date = db.Column(db.DateTime)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('links', lazy='dynamic'))

    def __init__(self, title, link, user):
        self.title = title
        self.link = link
        self.user = user

        self.date = datetime.utcnow()
   
    @classmethod
    def save(cls, *args):
        inst = cls(*args)
        session.add(inst)
        session.commit()

        return inst

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)



@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))
