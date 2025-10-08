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

def generate_booking_number():
    """Generate a unique booking number"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@main_bp.route('/')
def index():
    events = Event.query.all()
    print(f"Found {len(events)} events")

    return render_template('index.html', events=events)


@main_bp.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)

    # calculate remaining tickets dynamically.
    remaining = event.tickets_remaining

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

        # Add object to database
        db.session.add(seminar)
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
    db_upload_path = 'static/img/' + secure_filename(filename)
    # Save file and return db path
    fp.save(upload_path)

    return db_upload_path


@main_bp.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # check if event is sold out.
    if event.is_sold_out:
        flash('Sorry, this event is sold out!', 'danger')
        return redirect(url_for('main.event_details', event_id=event.id))

    qty = int(request.form.get('quantity', 1))
    
    # check if there are enough tickets.
    if qty > event.tickets_remaining:
        flash(f'Only {event.tickets_remaining} tickets remaining!', 'warning')
        return redirect(url_for('main.event_details', event_id=event.id))

    # generate unique booking number.
    booking_number = generate_booking_number()
    
    # check if booking number already exists (unlikely but safe).
    while Booking.query.filter_by(booking_number=booking_number).first():
        booking_number = generate_booking_number()

    booking = Booking(
        booking_number=booking_number,
        quantity=qty,
        booking_date=datetime.now(),
        status="Confirmed",
        user_id=current_user.id,
        event_id=event.id
    )
    
    db.session.add(booking)
    db.session.commit()

    flash(f'Booking confirmed! Your booking number is: {booking_number}', 'success')
    return redirect(url_for('main.event_details', event_id=event.id))

@main_bp.route('/bookings')
@login_required
def booking():
    """
    Takes the user to the bookings template. 
    
    This template contains all the confirmed and completed booked seminars that belong to a users account retrieved from the applications database and loads them into the bookings template.
    """

    # Get completed and confirmed bookings from database
    confirmed_bookings = Booking.query.filter(
        Booking.status == "Confirmed", 
        Booking.user_id == current_user.id
    ).all()
    
    completed_bookings = Booking.query.filter(
        Booking.status == 'Completed', 
        Booking.user_id == current_user.id
    ).all()
    
    cancelled_bookings = Booking.query.filter(
        Booking.status == 'Cancelled', 
        Booking.user_id == current_user.id
    ).all()

    return render_template(
        'bookings.html', 
        confirmed_bookings=confirmed_bookings, 
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings,
        heading='My Bookings | '
    )

@main_bp.route('/search')
def search():
    query = request.args.get('search').lower()
    
    # Get all possible results from page, seminars, comments, bookings and feed the data into the template
    return render_template('search.html', query=query, page_results = get_page_results(query), seminar_results = get_seminar_results(query), comment_results = get_comment_results(query), booking_results = get_booking_results(query))
    
@main_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # check if the current user owns this booking.
    if booking.user_id != current_user.id:
        flash('You can only cancel your own bookings.', 'danger')
        return redirect(url_for('main.booking'))
    
    # check if booking can be cancelled (only confirmed bookings).
    if booking.status != 'Confirmed':
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('main.booking'))
    
    # update booking status to cancelled.
    booking.status = 'Cancelled'
    db.session.commit()
    
    flash(f'Booking {booking.booking_number} has been cancelled successfully.', 'success')
    return redirect(url_for('main.booking'))

