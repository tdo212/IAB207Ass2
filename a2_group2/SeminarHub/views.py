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

