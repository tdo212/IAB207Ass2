from flask import Blueprint, flash, render_template, request, url_for, redirect, session
from .. import db
import os
from ..models import Event, Comment, Booking
from flask_login import login_required, current_user
from ..main.forms import EditForm, CreateForm
from datetime import datetime
from werkzeug.utils import secure_filename
from ..main.views import maybe_refresh_status, remaining_for, generate_booking_number

event_bp = Blueprint('event', __name__, template_folder='templates')


def check_upload_file(form) -> str:
    """Save uploaded image and return the DB path (served from /static/img/...)."""
    fp = form.image.data
    filename = secure_filename(fp.filename)
    base_path = os.path.dirname(__file__)
    upload_path = os.path.join(base_path, '..', 'static', 'img', filename)
    # DB path should be web-served path
    db_upload_path = f'/static/img/{filename}'
    fp.save(upload_path)
    return db_upload_path


@event_bp.route('/event/<int:event_id>')
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


@event_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Initialises the CreateForm for event creation.

    Retrieves the data from the form once the user hits submit and the form has been validated, creates an Event object and commits it to the database.
    """
    form = CreateForm()
    if form.validate_on_submit():
        db_file_path = check_upload_file(form)

        # Compile individual dates and times into datetime objects
        start_datetime = datetime.combine(form.start_date.data, form.start_time.data)
        end_datetime = datetime.combine(form.end_date.data, form.end_time.data)

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
        return redirect(url_for('event.create'))

    return render_template('create.html', form=form, heading='Create a Seminar | ')


@event_bp.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    is_sold_out = getattr(event, "is_sold_out", None)
    if callable(is_sold_out):
        if event.is_sold_out():
            flash('Sorry, this event is sold out!', 'danger')
            return redirect(url_for('event.event_details', event_id=event.id))
    elif hasattr(event, "is_sold_out"):
        if event.is_sold_out:
            flash('Sorry, this event is sold out!', 'danger')
            return redirect(url_for('event.event_details', event_id=event.id))

    qty = int(request.form.get('quantity', 1))
    remaining = remaining_for(event)
    if qty > remaining:
        flash(f'Only {remaining} tickets remaining!', 'warning')
        return redirect(url_for('event.event_details', event_id=event.id))

    booking = Booking(
        booking_number=generate_booking_number(),
        quantity=qty,
        booking_date=datetime.now(),
        status="Confirmed",
        user_id=current_user.id,
        event_id=event.id
    )
    db.session.add(booking)
    db.session.commit()

    maybe_refresh_status(event)

    flash(f'Booking confirmed! Your booking number is: {booking.booking_number}', 'success')
    return redirect(url_for('event.event_details', event_id=event.id))

# ----- Owner actions for events -----

@event_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Edits an already created event object if and only if the logged in users ID matches the event creators ID.

    Pre-fills out data in the form based on the data currently within the database.

    If form is validated, updates the database entries and commits it. 
    """
    # Get the seminar information from the database
    event = Event.query.get_or_404(event_id)

    # Check that the owner of the seminar is the one trying to access and edit it
    if current_user.id != event.owner_user_id:
        flash('You are not the owner of that seminar.', 'error')
        return redirect(url_for('event.event_details', event_id=event.id))
    
    # Pre-fill the form using the current seminars data
    form = EditForm(obj = event)


    if request.method == 'GET':
        # Gets the page the user was on prior to error
        back = request.referrer
        # If doesnt exist or it is itself, send back to details
        if back is None or request.url in back:
            back = url_for('event.event_details', event_id=event.id)
        # Store back url in session data to keep it present in case of validation error
        session['back'] = back
        
        # Pre-fill date/time fields on first load
        if event.start_dt and event.end_dt:
            try:
                form.start_date.data = event.start_dt.date()
                form.start_time.data = event.start_dt.time()
                form.end_time.data = event.end_dt.time()
                form.end_date.data = event.end_dt.date()
            except Exception:
                pass

    # If submitted which means request.method == 'POST', update database columns
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.category = form.category.data
        event.location = form.location.data
        event.capacity = form.capacity.data
        event.start_dt = datetime.combine(form.start_date.data, form.start_time.data)
        event.end_dt = datetime.combine(form.end_date.data, form.end_time.data)
        event.speaker = form.speaker.data
        event.speaker_bio = form.speaker_bio.data
        # Keep current image unless a new one is uploaded
        if getattr(form, "image", None) and getattr(form.image, "data", None) and getattr(form.image.data, "filename", ""):
            event.image_url = check_upload_file(form)
        
        db.session.commit()
        session.pop('back')
        
        maybe_refresh_status(event)
        flash(f'{event.title} successfully updated!', 'success')
        # Back to details page
        return redirect(url_for('event.event_details', event_id = event.id))

    return render_template('edit_seminar.html', form = form, event = event)


@event_bp.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_event(event_id):
    """Updates an event status to 'Cancelled' if and only if the logged in users ID matches the event creators ID. 
    """
    event = Event.query.get_or_404(event_id)
    
    if current_user.id != event.owner_user_id:
        flash('You are not the owner of that event.', 'error')
        return redirect(url_for('event.event_details', event_id=event.id))
    
    # Buttons should be disabled on events with these status, but as a fallback
    if event.status == 'Inactive' or event.status == 'Cancelled':
        flash('This event has finished or has already been cancelled.', 'error')
    else:
        # Change status
        event.status = "Cancelled"
        db.session.commit()
        flash('Event has been cancelled.', 'info')

    return redirect(url_for('event.event_details', event_id=event.id))

# ----- Comments -----

@event_bp.route('/event/<int:event_id>/comment', methods=['POST'])
@login_required
def add_comment(event_id):
    event = Event.query.get_or_404(event_id)

    text = (request.form.get('text') or '').strip()
    if not text:
        flash('Please enter a comment before posting.', 'warning')
        return redirect(url_for('event.event_details', event_id=event.id))
    if len(text) > 1000:
        flash('Comment is too long (max 1000 characters).', 'warning')
        return redirect(url_for('event.event_details', event_id=event.id))

    comment = Comment(text=text, user_id=current_user.id, event_id=event.id)
    db.session.add(comment)
    db.session.commit()

    flash('Comment posted!', 'success')
    return redirect(url_for('event.event_details', event_id=event.id))

@event_bp.route('/event/<int:event_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(event_id, comment_id):
    """Delete a comment if the current user is the owner."""
    comment = Comment.query.get_or_404(comment_id)

    # Check ownership
    if comment.user_id != current_user.id:
        flash('You can only delete your own comments.', 'warning')
        return redirect(url_for('event.event_details', event_id=event_id))

    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.', 'success')
    return redirect(url_for('event.event_details', event_id=event_id))
