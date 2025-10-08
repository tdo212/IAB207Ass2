from flask import Blueprint, render_template, redirect, request, url_for, flash
from .forms import CreateForm
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from . import db
from .models import Event, Booking
from datetime import datetime
from .search_functions import *

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """  Added for testing purposes only - adds a mock event to the database (to see if it displays on index.html)
     new_event = Event(title = 'Test', description = 'Exploring the latest advancements in AI and machine learning technologies.', category = 'cs', location = 'Main Auditorium', capacity = 20, start_dt = datetime(2025, 10, 15, 14, 0, 0), end_dt = datetime(2025, 10, 15, 14, 0, 0), image_url = 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80', speaker = 'Ash', owner_user_id = 1)
     db.session.add(new_event)
     db.session.commit() """

    events = Event.query.all()  # This will now return 6 events
    print(f"Found {len(events)} events")  # Should print "Found 6 events"
    return render_template('index.html', events=events)

@main_bp.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)

    remaining = max(0, event.capacity or 0)

    comments = getattr(event, "comments", [])

    return render_template(
        'details.html',
        event=event,
        remaining=remaining,
        comments=comments,
        heading='Event Details | '
    )
    """  Added for testing purposes only - adds a mock event to the database (to see if it displays on index.html)
     new_event = Event(title = 'Test', description = 'Exploring the latest advancements in AI and machine learning technologies.', category = 'cs', location = 'Main Auditorium', capacity = 20, start_dt = datetime(2025, 10, 15, 14, 0, 0), end_dt = datetime(2025, 10, 15, 14, 0, 0), image_url = 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80', speaker = 'Ash', owner_user_id = 1)
     db.session.add(new_event)
     db.session.commit() """

    events = Event.query.all()  # This will now return 6 events
    print(f"Found {len(events)} events")  # Should print "Found 6 events"
    return render_template('index.html', events=events)

@main_bp.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)

    remaining = max(0, event.capacity or 0)

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

        # Create seminar object
        seminar = Event(title = form.title.data, description = form.description.data, category = form.category.data, location = form.location.data, capacity = form.capacity.data, start_dt = start_datetime, end_dt = end_datetime, image_url = db_file_path, speaker = form.speaker.data, speaker_bio = form.speaker_bio.data, owner_user_id = current_user.id )

        # Add object to database
        db.session.add(seminar)

        # Commit to database
        db.session.commit()

        flash('Successfully created new seminar', 'success')
        
        return redirect(url_for('main.create'))
    return render_template('create.html', form = form, heading = 'Create a Seminar | ')

def check_upload_file(form):
    # Form file data
    fp = form.image.data
    filename = fp.filename
    # Gets relative current path of the module file 
    BASE_PATH = os.path.dirname(__file__)
    # Upload path = static/img
    upload_path = os.path.join(BASE_PATH, 'static/img', secure_filename(filename))
    # Store relative upload path into DB as image location
    db_upload_path = 'static/img' + secure_filename(filename)
    # Save file and return db path
    fp.save(upload_path)

    return db_upload_path

@main_bp.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)

    qty = int(request.form.get('quantity', 1))

    booking = Booking(
        quantity=qty,
        booking_date=datetime.utcnow(),
        status="Confirmed",
        user_id=current_user.id,
        event_id=event.id
    )
    db.session.add(booking)
    db.session.commit()

    flash(f'Registered for "{event.title}" (x{qty}).', 'success')
    return redirect(url_for('main.event_details', event_id=event.id))

@main_bp.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)

    qty = int(request.form.get('quantity', 1))

    booking = Booking(
        quantity=qty,
        booking_date=datetime.utcnow(),
        status="Confirmed",
        user_id=current_user.id,
        event_id=event.id
    )
    db.session.add(booking)
    db.session.commit()

    flash(f'Registered for "{event.title}" (x{qty}).', 'success')
    return redirect(url_for('main.event_details', event_id=event.id))

@main_bp.route('/bookings')
@login_required
def booking():
    """
    Takes the user to the bookings template. 
    
    This template contains all the confirmed and completed booked seminars that belong to a users account retrieved from the applications database and loads them into the bookings template.

    """

    # Get completed and confirmed bookings from database
    confirmed_bookings = Booking.query.filter(Booking.status == "Confirmed", Booking.user_id == current_user.id).all()
    completed_bookings = Booking.query.filter(Booking.status == 'Completed', Booking.user_id == current_user.id).all()

    return render_template('bookings.html', confirmed_bookings=confirmed_bookings, completed_bookings=completed_bookings, heading = 'My Bookings | ')

@main_bp.route('/search')
def search():
    query = request.args.get('search').lower()
    
    # Get all possible results from page, seminars, comments, bookings and feed the data into the template
    return render_template('search.html', query=query, page_results = get_page_results(query), seminar_results = get_seminar_results(query), comment_results = get_comment_results(query), booking_results = get_booking_results(query))
    

