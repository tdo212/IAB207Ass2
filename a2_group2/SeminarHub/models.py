from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    """
    Represents a user in the application.

    Stores the user information in seperate columns within the database using an incrementing ID as the primary key.
    """
    __tablename__ = 'users' 

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
    status = db.Column(db.String(16), default="Open")  
    start_dt = db.Column(db.DateTime, nullable=False)
    end_dt = db.Column(db.DateTime, nullable=False)
    image_url = db.Column(db.String(255))
    speaker = db.Column(db.String(120))
    speaker_bio = db.Column(db.Text)

    # who created/owns the event 
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = db.relationship("User", backref="owned_events")

    # relationships
    comments = db.relationship("Comment", back_populates="event", cascade="all, delete-orphan")
    orders = db.relationship("Order", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event {self.title}>"

# Comment model
class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    user = db.relationship("User", backref="comments")
    event = db.relationship("Event", back_populates="comments")

    def __repr__(self):
        return f"<Comment {self.id} on Event {self.event_id}>"

# class Order(db.Model):
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    ticket_type = db.Column(db.String(64), default="General Admission")
    total_price = db.Column(db.Float, default=0.0)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    user = db.relationship("User", backref="orders")
    event = db.relationship("Event", back_populates="orders")

    def __repr__(self):
        return f"<Order {self.id} x{self.quantity} event={self.event_id}>"

# Booking model
class Booking(db.Model):
    """
    Represents a Booking in the application.

    Stores the Booking information in seperate columns within the database using an incrementing ID as the primary key.

    Uses Event ID and User ID as foreign keys for this table.
    """

    tablename = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(32), index=True, unique=True)
    # This is duplicated in both Order and Booking. Might need to remove one and make it a relational entry once 'Details' view is completed
    quantity = db.Column(db.Integer, index=True, nullable=False) 
    booking_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(32), default="Confirmed")

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    def repr(self):
        """
        String representation of the Booking model for development purposes.
        """
        return '<Booking ID: {}, Booking Number: {}, Quantity: {}, Booking Date: {}, Status: {}>'.format(self.id, self.booking_number, self.quantity, self.booking_date, self.status) 
