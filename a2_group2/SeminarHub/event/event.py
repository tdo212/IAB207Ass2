from flask import Blueprint, flash, render_template, request, url_for, redirect
from .. import db
from ..models import Event, Comment, Booking
from flask_login import login_required, current_user
from ..forms import EditForm, CreateForm
from datetime import datetime
from ..views import check_upload_file, maybe_refresh_status, remaining_for, generate_booking_number

event_bp = Blueprint('event', __name__, template_folder='templates')


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

    flash('Booking confirmed!', 'success')
    return redirect(url_for('event.event_details', event_id=event.id))

# ----- Owner actions for events -----

@event_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    # Get the seminar information from the database
    event = Event.query.get_or_404(event_id)

    # Check that the owner of the seminar is the one trying to access and edit it
    if current_user.id != event.owner_user_id:
        flash('You are not the owner of that seminar.', 'error')
        return redirect(url_for('event.event_details', event_id=event.id))
    
    # Pre-fill the form using the current seminars data
    form = EditForm(obj = event)

    # Pre-fill date/time fields on first load
    if request.method == 'GET' and event.start_dt and event.end_dt:
        try:
            form.date.data = event.start_dt.date()
            form.start_time.data = event.start_dt.time()
            form.end_time.data = event.end_dt.time()
        except Exception:
            pass

    # If submitted which means request.method == 'POST', update database columns
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.category = form.category.data
        event.location = form.location.data
        event.capacity = form.capacity.data
        event.start_dt = datetime.combine(form.date.data, form.start_time.data)
        event.end_dt = datetime.combine(form.date.data, form.end_time.data)
        event.speaker = form.speaker.data
        event.speaker_bio = form.speaker_bio.data
        # Keep current image unless a new one is uploaded
        if getattr(form, "image", None) and getattr(form.image, "data", None) and getattr(form.image.data, "filename", ""):
            event.image_url = check_upload_file(form)
        
        db.session.commit()
        
        maybe_refresh_status(event)
        flash(f'{event.title} successfully updated!', 'success')
        # Back to details page
        return redirect(url_for('event.event_details', event_id = event.id))

    return render_template('edit_seminar.html', form = form, event = event)


@event_bp.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if current_user.id != event.owner_user_id:
        flash('You are not the owner of that event.', 'error')
        return redirect(url_for('event.event_details', event_id=event.id))
    
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