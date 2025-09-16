from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    """
    Represents a user in the application.

    Stores the user information in seperate columns within the database using an incrementing ID as the primary key.
    """

    # TODO: Add table name when database integrated into app
    __tablename__ = 'TABLE NAME HERE' 

    # TODO: Uncomment this out when database is integrated into app
    # User model inputs into database columns
    # id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(64), unique=True, index=True)
    # email = db.Column(db.String(64), unique=True)
    # password_hash = db.Column(db.String(256), nullable=False)
    # number = db.Column(db.String(64), nullable=False)
    # address = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """
        String representation of the User model for development purposes.
        """
        return '<User: {}>'.format(self.name)

class Event(db.Model):

class Comment(db.Model):

class Order(db.Model):