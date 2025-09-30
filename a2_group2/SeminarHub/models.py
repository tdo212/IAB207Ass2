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

    # TODO: Implement database for this to work
    # User model inputs into database columns
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    number = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """
        String representation of the User model for development purposes.
        """
        return '<User: {}>'.format(self.name)

# class Event(db.Model):

# class Comment(db.Model):

# class Order(db.Model):