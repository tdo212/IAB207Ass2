from flask import Blueprint, render_template, redirect, request, url_for, flash
from .forms import CreateForm
import os, random, string
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from . import db
from .models import Event, Booking, Comment
from datetime import datetime
from .search_functions import *

main_bp = Blueprint('main', __name__)

# ---------- helpers ----------

def generate_booking_number(length: int = 8) -> str:
    """Generate a unique booking number (A–Z, 0–9)."""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=length))
    # In the unlikely case of a collision, regenerate
    while Booking.query.filter_by(booking_number=code).first():
        code = ''.join(random.choices(chars, k=length))
    return code

def remaining_for(event: Event) -> int:
    """
    Get remaining capacity using whichever API the model provides:
    - teammate: event.tickets_remaining
    - yours: event.remaining_capacity()
    - fallback: event.capacity
    """
    if hasattr(event, "tickets_remaining"):
        return max(0, int(event.tickets_remaining or 0))
    if hasattr(event, "remaining_capacity"):
        try:
            return max(0, int(event.remaining_capacity() or 0))
        except TypeError:
            pass
    return max(0, int(event.capacity or 0))

def maybe_refresh_status(event: Event) -> None:
    """
    If your model has ensure_fresh_status(), use it. Otherwise noop.
    This lets status auto-update when viewing/booking.
    """
    if hasattr(event, "ensure_fresh_status"):
        try:
            if event.ensure_fresh_status():
                db.session.commit()
        except Exception:
            pass

def check_upload_file(form) -> str:
    """Save uploaded image and return the DB path (served from /static/img/...)."""
    fp = form.image.data
    filename = secure_filename(fp.filename)
    base_path = os.path.dirname(__file__)
    upload_path = os.path.join(base_path, 'static', 'img', filename)
    # DB path should be web-served path
    db_upload_path = f'/static/img/{filename}'
    fp.save(upload_path)
    return db_upload_path

# ---------- routes ----------

@main_bp.route('/')
def index():
    events = Event.query.all()
    any_changed = False
    for e in events:
        if hasattr(e, "ensure_fresh_status"):
            try:
                if e.ensure_fresh_status():
                    any_changed = True
            except Exception:
                pass
    if any_changed:
        db.session.commit()
    return render_template('index.html', events=events)

@main_bp.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)

    remaining = remaining_for(event)
    maybe_refresh_status(event)

    comments = getattr(event, "comments", [])

    return render_template(
        'details.html',
        event=event,
        remaining=remaining,
        comments=comments,
        heading='Event Details | '
    )

@main_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateForm()
    if form.validate_on_submit():
        db_file_path = check_upload_file(form)

        # Compile individual dates and times into datetime objects
        start_datetime = datetime.combine(form.date.data, form.start_time.data)
        end_datetime = datetime.combine(form.date.data, form.end_time.data)

        seminar = Event(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            location=form.location.data,
            capacity=form.capacity.data,
            start_dt=start_datetime,
            end_dt=end_datetime,
            image_url=db_file_path,
            speaker=form.speaker.data,
            speaker_bio=form.speaker_bio.data,
            owner_user_id=current_user.id
        )

        db.session.add(seminar)
        db.session.commit()

        flash('Successfully created new seminar', 'success')
        return redirect(url_for('main.create'))

    return render_template('create.html', form=form, heading='Create a Seminar | ')

@main_bp.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    is_sold_out = getattr(event, "is_sold_out", None)
    if callable(is_sold_out):
        if event.is_sold_out():
            flash('Sorry, this event is sold out!', 'danger')
            return redirect(url_for('main.event_details', event_id=event.id))
    elif hasattr(event, "is_sold_out"):
        if event.is_sold_out:
            flash('Sorry, this event is sold out!', 'danger')
            return redirect(url_for('main.event_details', event_id=event.id))

    qty = int(request.form.get('quantity', 1))
    remaining = remaining_for(event)
    if qty > remaining:
        flash(f'Only {remaining} tickets remaining!', 'warning')
        return redirect(url_for('main.event_details', event_id=event.id))

    booking = Booking(
        booking_number=generate_booking_number(),
        quantity=qty,
        booking_date=datetime.utcnow(),
        status="Confirmed",
        user_id=current_user.id,
        event_id=event.id
    )
    db.session.add(booking)
    db.session.commit()

    maybe_refresh_status(event)

    flash('Booking confirmed!', 'success')
    return redirect(url_for('main.event_details', event_id=event.id))

@main_bp.route('/bookings')
@login_required
def booking():
    """User’s bookings, split by status."""
    confirmed_bookings = Booking.query.filter(
        Booking.status == "Confirmed",
        Booking.user_id == current_user.id
    ).all()

    completed_bookings = Booking.query.filter(
        Booking.status == "Completed",
        Booking.user_id == current_user.id
    ).all()

    cancelled_bookings = Booking.query.filter(
        Booking.status == "Cancelled",
        Booking.user_id == current_user.id
    ).all()

    return render_template(
        'bookings.html',
        confirmed_bookings=confirmed_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings,
        heading='My Bookings | '
    )

@main_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking (only if you own it and it’s Confirmed)."""
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash('You can only cancel your own bookings.', 'danger')
        return redirect(url_for('main.booking'))

    if booking.status != 'Confirmed':
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('main.booking'))

    booking.status = 'Cancelled'
    db.session.commit()
    flash(f'Booking {booking.booking_number} has been cancelled.', 'success')
    return redirect(url_for('main.booking'))

# ----- Owner actions for events -----

@main_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.owner_user_id != current_user.id:
        flash('You are not authorised to edit this event.', 'danger')
        return redirect(url_for('main.event_details', event_id=event.id))

    form = CreateForm(obj=event)

    # Pre-fill date/time fields on first load
    if request.method == 'GET' and event.start_dt and event.end_dt:
        try:
            form.date.data = event.start_dt.date()
            form.start_time.data = event.start_dt.time()
            form.end_time.data = event.end_dt.time()
        except Exception:
            pass

    if form.validate_on_submit():
        # Keep current image unless a new one is uploaded
        if getattr(form, "image", None) and getattr(form.image, "data", None) and getattr(form.image.data, "filename", ""):
            event.image_url = check_upload_file(form)

        event.title = form.title.data
        event.description = form.description.data
        event.category = form.category.data
        event.location = form.location.data
        event.capacity = form.capacity.data
        event.speaker = form.speaker.data
        event.speaker_bio = form.speaker_bio.data

        if form.date.data and form.start_time.data and form.end_time.data:
            event.start_dt = datetime.combine(form.date.data, form.start_time.data)
            event.end_dt = datetime.combine(form.date.data, form.end_time.data)

        db.session.commit()
        maybe_refresh_status(event)
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.event_details', event_id=event.id))

    return render_template('edit_seminar.html', form=form, seminar=event, heading='Edit Seminar | ')

@main_bp.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.owner_user_id != current_user.id:
        flash('You are not authorised to cancel this event.', 'danger')
        return redirect(url_for('main.event_details', event_id=event.id))

    event.status = 'Cancelled'
    db.session.commit()
    flash('Event has been cancelled.', 'info')
    return redirect(url_for('main.event_details', event_id=event.id))

# ----- Comments -----

@main_bp.route('/event/<int:event_id>/comment', methods=['POST'])
@login_required
def add_comment(event_id):
    event = Event.query.get_or_404(event_id)

    text = (request.form.get('text') or '').strip()
    if not text:
        flash('Please enter a comment before posting.', 'warning')
        return redirect(url_for('main.event_details', event_id=event.id))
    if len(text) > 1000:
        flash('Comment is too long (max 1000 characters).', 'warning')
        return redirect(url_for('main.event_details', event_id=event.id))

    comment = Comment(text=text, user_id=current_user.id, event_id=event.id)
    db.session.add(comment)
    db.session.commit()

    flash('Comment posted!', 'success')
    return redirect(url_for('main.event_details', event_id=event.id))

# ----- Search -----

@main_bp.route('/search')
def search():
    query = (request.args.get('search') or '').lower()
    return render_template(
        'search.html',
        query=query,
        page_results=get_page_results(query),
        seminar_results=get_seminar_results(query),
        comment_results=get_comment_results(query),
        booking_results=get_booking_results(query),
    )

