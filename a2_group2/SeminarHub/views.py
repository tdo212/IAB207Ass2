from flask import Blueprint, render_template, request, redirect, url_for
import os, random, string
from werkzeug.utils import secure_filename
from . import db
from .models import Event, Booking
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
    selected_category = request.args.get('category', None)
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
    if selected_category:
        events = Event.query.filter_by(category=selected_category).all()
    else:
        events = Event.query.all()
    recent_cutoff = datetime.now().date()
    recently_added = [event for event in events if (recent_cutoff - event.date_added.date()).days <= 7]

    categories = db.session.query(Event.category).distinct().all()
    categories = [category[0] for category in categories]


    return render_template('index.html', events=events, categories = categories, selected_category=selected_category, recently_added=recently_added)


# ----- Search -----

@main_bp.route('/search')
def search():
    """Processes the users search query with the help of multiple helper functions in order to retrieve all possible database entries that match or partially match that query.

    Then renders the results on the main search page along with the raw search query as entered by the user.
    """
    # For displaying the exact user input in the HTML template
    raw_query = (request.args.get('search') or '').strip()
    query = raw_query.lower()

    # Search for date
    if query:
        query = date_search(query)

    # Search for time next
        if ':' in query:
            query = time_search(query)

    return render_template(
        'search.html',
        raw_query = raw_query,
        query=query,
        page_results=get_page_results(query),
        seminar_results=get_seminar_results(query),
        comment_results=get_comment_results(query),
        booking_results=get_booking_results(query),
    )

