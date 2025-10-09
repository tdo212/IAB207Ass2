from flask import Blueprint, flash, render_template, request, url_for, redirect
from .. import db
from ..models import Event
from flask_login import login_required, current_user

user_bp = Blueprint('user', __name__, template_folder='templates')

# TODO: Complete the profile page rendering here if we have time
# @event_bp.route('/profile/<user_id>')
# def profile(user_id):


@user_bp.route('/profile/<int:user_id>/events')
@login_required
def events(user_id):
    events = db.session.query(Event).filter(Event.owner_user_id == user_id).all()

    return render_template('my_seminars.html', seminars = events, heading = 'My Seminars | ')