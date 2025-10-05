from flask import Blueprint, render_template, redirect, request, url_for, flash
from .forms import CreateForm
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from . import db
from .models import Event, Booking
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    events = Event.query.all()  # This will now return 6 events
    print(f"Found {len(events)} events")  # Should print "Found 6 events"
    return render_template('index.html', events=events)

@main_bp.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('details.html', event=event, heading='Event Details | ')


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

@main_bp.route('/bookings')
@login_required
def booking():
    """
    Takes the user to the bookings template. 
    
    This template contains all the booked seminars that belong to a users account retrieved from the applications database.

    """

    """    
    BELOW IS FOR TESTING PURPOSES ONLY

    ADDS A MOCK EVENT AND BOOKING TO THE DATABASE

    UNCOMMENT IT WHEN YOU NEED TO ADD IT BACK INTO THE DATABSE OR COMMENT IT OUT WHEN YOU DON'T
    
    REMOVE THIS SECTION ONCE DATABASE STUFF HAS BEEN FULLY INTEGRATED
    """
    # start_datetime = datetime.strptime('10 15, 2025 14:00', '%m %d, %Y %H:%M')
    # end_datetime = datetime.strptime('10 15, 2025 15:00', '%m %d, %Y %H:%M')

    # new_event = Event(title = 'Future of Artificial Intelligence', description = 'Exploring the latest advancements in AI and machine learning technologies.', category = 'cs', location = 'Main Auditorium', capacity = 20, start_dt = start_datetime, end_dt = end_datetime, image_url = 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80', speaker = 'Ash', owner_user_id = 1)
    # print("Event added.")


    # b_date = datetime.strptime('09 28, 2023 10:00', '%m %d, %Y %H:%M')
    # new_booking = Booking(booking_number = 'SH789456', quantity = 2, booking_date = b_date, status = "Confirmed", user_id = 1, event = new_event)
    # print("booking added.")

    # # Add to database
    # db.session.add(new_event)
    # db.session.add(new_booking)
    # db.session.commit()
    # print('booking and event commmited to database')

    # Get all bookings from database
    bookings = Booking.query.all()


    return render_template('bookings.html', bookings = bookings, heading = 'My Bookings | ')
