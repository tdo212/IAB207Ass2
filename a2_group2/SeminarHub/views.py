from flask import Blueprint, render_template, redirect, request, url_for
from .forms import CreateForm
import os
from werkzeug.utils import secure_filename

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/create', methods=['GET', 'POST'])
def create():
    form = CreateForm()
    if form.validate_on_submit():
        db_file_path = check_upload_file(form)
        # Create seminar class object here including image = db_file_path
        # seminar = Seminar()

        # Add object to database
        # db.session.add(seminar)

        # Commit to database
        # db.session.commit()
        print('Successfully created new seminar', 'success')
        return redirect(url_for('main.create'))
    return render_template('create.html', form = form)

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
def booking():
    return render_template('bookings.html')

@main_bp.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    comments = event.comments
    remaining = max(0, event.capacity or 0)  

    comment_form = CommentForm()
    ticket_form = TicketForm()

    # Handle comment submission
    if request.method == 'POST' and comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Please log in to comment.', 'warning')
            return redirect(url_for('auth.login'))
        new_comment = Comment(
            text=comment_form.text.data,
            user_id=current_user.id,
            event_id=event.id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment posted!', 'success')
        return redirect(url_for('main.event_details', event_id=event.id))

    return render_template(
        'details.html',
        event=event,
        comments=comments,
        remaining=remaining,
        comment_form=comment_form,
        ticket_form=ticket_form
    )


@main_bp.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    # create a booking/order object here
    flash('Registration not implemented yet.')
    return redirect(url_for('main.event_details', event_id=event_id))
