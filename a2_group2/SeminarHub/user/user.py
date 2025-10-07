from flask import Blueprint, flash, render_template, request, url_for, redirect
from .. import db
from ..models import Event
from flask_login import login_required, current_user
from ..forms import EditForm
from datetime import datetime
from ..views import check_upload_file

user_bp = Blueprint('user', __name__, template_folder='templates')

# TODO: Complete the profile page rendering here
# @user_bp.route('/user/<user_id>')
# def user(user_id):


@user_bp.route('/user/<int:user_id>/seminars')
@login_required
def seminars(user_id):
    seminars = db.session.query(Event).filter(Event.owner_user_id == user_id).all()

    return render_template('my_seminars.html', seminars = seminars, heading = 'My Seminars - ')

@user_bp.route('/edit_seminar/<int:seminar_id>', methods=['GET', 'POST'])
@login_required
def edit_seminar(seminar_id):
    # Get the seminar information from the database
    seminar = db.session.query(Event).filter(Event.id == seminar_id).first()

    # Check that the owner of the seminar is the one trying to access and edit it
    if current_user.id != seminar.owner_user_id:
        flash('You are not the owner of that seminar.', 'error')
        return redirect(url_for('main.index'))
    
    # Pre-fill the form using the current seminars data
    form = EditForm(obj = seminar)

    # If submitted which means request.method == 'POST', update database columns
    if form.validate_on_submit():
        seminar.title = form.title.data
        seminar.description = form.description.data
        seminar.category = form.category.data
        seminar.location = form.location.data
        seminar.capacity = form.capacity.data
        seminar.start_dt = datetime.combine(form.date.data, form.start_time.data)
        seminar.end_dt = datetime.combine(form.date.data, form.end_time.data)
        seminar.speaker = form.speaker.data
        seminar.speaker_bio = form.speaker_bio.data
        # If new image uploaded, update image
        if form.image.data:
            seminar.image_url = check_upload_file(form)
        # Commit to database
        db.session.commit()

        flash('Successfully updated seminar {}', 'success').format(seminar.title)

        # Back to user seminars page
        return redirect(url_for('user.seminars', user_id=current_user.id))

    # If user loads page meaning request.method == 'GET', manually fill date and time form fields because database type is DateTime
    elif request.method == 'GET':
        form.date.data = seminar.start_dt.date()
        form.start_time.data = seminar.start_dt.time()
        form.end_time.data = seminar.end_dt.time()


    return render_template('edit_seminar.html', form = form, seminar = seminar)

# Handle cancelling of event here
@user_bp.route('/cancel_seminar/<int:seminar_id>')
@login_required
def cancel(seminar_id):
    seminar = db.session.query(Event).filter(Event.id == seminar_id).first()
    
    if current_user.id != seminar.owner_user_id:
        flash('You are not the owner of that seminar.', 'error')
        return redirect(url_for('main.index'))
    
    # Change status
    seminar.status = "Cancelled"
    # Commit
    db.session.commit()

    return render_template('index.html')