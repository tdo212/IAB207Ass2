from flask import Blueprint, flash, render_template, url_for, redirect
from .. import db
from ..models import Event, User, Comment
from flask_login import login_required, current_user
from ..main.forms import EditProfileForm

user_bp = Blueprint('user', __name__, template_folder='templates')


@user_bp.route('/profile/<user_id>')
@login_required
def profile(user_id):
    """
    Accesses the user object from the database based on the user_id entered which is obtained via the LoginManager current_user.
    """
    user = User.query.filter_by(id = current_user.id).first()
        
    return render_template('profile.html', heading = 'Profile | ', user = user, details_template = '_account_details.html')


@user_bp.route('/profile/edit_profile/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    """Accesses the user object from the database and pre-fills a form from that object.

    If there are no validation errors when the form is submitted, will commit the new user data to the database.

    Email is not able to be edited in this form as it is the user's login and should not be altered.
    """
    user = User.query.filter_by(id = current_user.id).first()

    # Pre-fill existing user information
    edit_form = EditProfileForm(obj = user)

    if edit_form.validate_on_submit():
        # Update details if form valid
        user.first_name = edit_form.first_name.data
        user.last_name = edit_form.last_name.data
        user.email = edit_form.email.data
        user.number = edit_form.number.data
        user.address = edit_form.address.data

        db.session.commit()

        flash('User details updated', 'success')

        return redirect(url_for('user.profile', user_id = current_user.id))

    return render_template('profile.html', heading = 'Edit Profile | ', user = user, edit_form = edit_form, details_template = '_edit_account_details.html')


@user_bp.route('/profile/<int:user_id>/events')
@login_required
def events(user_id):
    """
    Loads the users created events from the database into the main content area of the profile template.
    """
    events = db.session.query(Event).filter(Event.owner_user_id == user_id).all()

    return render_template('my_seminars.html', seminars = events, heading = 'My Seminars | ')


@user_bp.route('/profile/<int:user_id>/comments')
@login_required
def comments(user_id):
    """
    Loads the users created comments from the database into the main content area of the profile template.
    """
    comments = db.session.query(Comment).filter(Comment.user_id == user_id).all()

    return render_template('my_comments.html', comments = comments, heading = 'My Comments | ')