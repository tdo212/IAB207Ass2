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

# Event model
class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64))
    location = db.Column(db.String(120))
    capacity = db.Column(db.Integer, default=0)
    status = db.Column(db.String(16), default="Open")  # Open, Inactive, Sold Out, Cancelled
    start_dt = db.Column(db.DateTime, nullable=False)
    end_dt = db.Column(db.DateTime, nullable=False)
    image_url = db.Column(db.String(255))

    # Relationships
    comments = db.relationship("Comment", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event {self.title}>"

# Comment model
class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    # Relationships
    user = db.relationship("User", backref="comments")
    event = db.relationship("Event", back_populates="comments")

    def __repr__(self):
        return f"<Comment {self.id} on Event {self.event_id}>"

# class Order(db.Model):
