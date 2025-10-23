from . import db
from datetime import datetime, timezone
from flask_login import UserMixin

# User ---------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name  = db.Column(db.String(64), index=True)
    email      = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    number     = db.Column(db.String(64), nullable=False)
    address    = db.Column(db.String(256), nullable=False)
    
    # Utility
    last_seen = db.Column(db.DateTime, default=datetime.now())

    # Relationships
    bookings      = db.relationship("Booking", back_populates="user")
    comments      = db.relationship("Comment", back_populates="user")
    owned_events  = db.relationship("Event",   back_populates="owner")

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name} ({self.email})>"
        
# Event ---------------------------
class Event(db.Model):
    __tablename__ = "events"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category    = db.Column(db.String(64))
    location    = db.Column(db.String(120))
    capacity    = db.Column(db.Integer, default=0)
    status      = db.Column(db.String(16), default="Open")
    start_dt    = db.Column(db.DateTime, nullable=False)
    end_dt      = db.Column(db.DateTime, nullable=False)
    image_url   = db.Column(db.String(255))
    speaker     = db.Column(db.String(120))
    speaker_bio = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Owner
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner         = db.relationship("User", back_populates="owned_events")

    # Relationships
    comments = db.relationship(
        "Comment",
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="desc(Comment.created_at)"  
    )
    bookings = db.relationship(
        "Booking",
        back_populates="event",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Event {self.title}>"
        
    @property
    def tickets_remaining(self) -> int:
        """Remaining tickets ignoring cancelled bookings."""
        total_booked = sum(b.quantity or 0 for b in self.bookings if (b.status or "") != "Cancelled")
        return max(0, (self.capacity or 0) - total_booked)

    @property
    def is_sold_out(self) -> bool:
        return self.tickets_remaining <= 0

    def seats_taken(self) -> int:
        """Confirmed seats taken (backwards compatible with any existing use)."""
        return sum(b.quantity or 0 for b in self.bookings if (b.status or "").lower() == "confirmed")

    def remaining_capacity(self) -> int:
        """Alias kept for any existing templates/calls."""
        return self.tickets_remaining

    def compute_status(self) -> str:
        """Derive the status based on time/capacity unless Cancelled."""
        if (self.status or "").lower() == "cancelled":
            return "Cancelled"
        now = datetime.utcnow()
        if self.end_dt and now >= self.end_dt:
            return "Inactive"
        if self.tickets_remaining == 0:
            return "Sold Out"
        return "Open"

    def ensure_fresh_status(self) -> bool:
        """Update status if stale. Returns True if it changed."""
        new_status = self.compute_status()
        if new_status != (self.status or "Open"):
            self.status = new_status
            return True
        return False

# Comment ---------------------------
class Comment(db.Model):
    __tablename__ = "comments"

    id         = db.Column(db.Integer, primary_key=True)
    text       = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id  = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    user  = db.relationship("User",  back_populates="comments")
    event = db.relationship("Event", back_populates="comments")

    def __repr__(self):
        return f"<Comment {self.id} on Event {self.event_id}>"

# Booking ---------------------------
class Booking(db.Model):
    __tablename__ = 'bookings'

    id             = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(32), index=True, unique=True)
    quantity       = db.Column(db.Integer, index=True, nullable=False)
    booking_date   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status         = db.Column(db.String(32), default="Confirmed")

    user_id  = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    user  = db.relationship("User",  back_populates="bookings")
    event = db.relationship("Event", back_populates="bookings")

    def __repr__(self):
        return f"<Booking {self.id} #{self.booking_number} qty={self.quantity} status={self.status}>"