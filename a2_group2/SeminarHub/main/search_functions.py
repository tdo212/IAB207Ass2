"""
This file contains helper functions that enable the search bar to work.
"""
from ..models import Event, Booking, Comment, User
from flask_login import current_user
from sqlalchemy import or_, cast, String
from datetime import datetime

def search_table(model, columns, search_query):
    """
    Parses through each column of a given database table using pythons built in getattr() method, attempts to match a case insensitive (ilike) query and then returns all rows that match that query from the table.

    If a column is type datetime, first cast it into a string and then complete the search as datetime is the only type that does not work with the original search functionality.

    Taken and modified from: https://stackoverflow.com/a/57192587 and https://stackoverflow.com/a/42780340
    """
    sql_queries = []

    for col in columns:
        # Get the table and column object for each col e.g. Event.title
        col_object = getattr(model, col)

        # If object type == DatetTIme
        if col_object.type.python_type == datetime:
            # If search query has been passed through as a list indicates it's from date_search and therefore is a day + month search
            if type(search_query) is list:
                for query in search_query:
                    # Cast column to type String and search
                    sql_queries.append(cast(col_object, String).ilike(f'%{query}%'))
            else:
                # If not a list, indicates it's just a month or day or year individually
                sql_queries.append(cast(col_object, String).ilike(f'%{search_query}%'))
        else:
            # Otherwise search like normal
            sql_queries.append(col_object.ilike(f'%{search_query}%'))
    
    return model.query.filter(or_(*sql_queries)).all()


def get_page_results(search_query):
    """
    Creates multiple dictionaries that have key words that might be related to distinct pages in the web application.

    If the search query is one of these key words, return a list containing the dictionary.

    If no key words detected, return an empty list.
    """

    # Page dictionaries
    bookings = {'name': 'My Bookings', 'link':'booking.booking', 'searchable_words':['book', 'booking', 'my booking', 'my bookings', 'bookings']}
    user = {'name': 'Profile', 'link':'user.events', 'searchable_words':['profile', 'my profile', 'my account', 'account', 'my seminars', 'my events', 'events']}
    create = {'name': 'Create Event', 'link': 'event.create', 'searchable_words':['create', 'create seminar', 'create event', 'create new']}

    page_results = []

    # Search for bookings keywords
    if search_query in bookings['searchable_words']:
        page_results.append(bookings)
    # Search for user / profile keywords
    elif search_query in user['searchable_words']:
        page_results.append(user)
    # Search for create keywords
    elif search_query in create['searchable_words']:
        page_results.append(create)
        
    return page_results


def get_seminar_results(search_query):
    """
    Uses the search_table() function to query each column within the Event table and return results as a list if they match the search query.

    If no results found, returns an empty list.
    """
    seminar_columns = [
        "title",
        "description",
        "category",
        "location",
        "capacity",
        "status",
        "start_dt",
        "end_dt",
        "speaker",
        "speaker_bio"
    ]

    seminar_results = search_table(Event, seminar_columns, search_query)

    return seminar_results


def get_comment_results(search_query):
    """
    Handles searches for comments.

    Uses the search_table() function to query columns within the Comment table and the User table and return results as a list if they match the search query.

    If no results found, returns an empty list.
    """
    comment_columns = [
        "text",
        "created_at"
    ]
    user_columns = [
        "first_name",
        "last_name"
    ]

    # Get users based on first or last name only. Avoid sensitive information.
    user_results = search_table(User, user_columns, search_query)

    comments = search_table(Comment, comment_columns, search_query)

    related_comments = []

    if user_results:
        for user in user_results:
            # Get comments that are made by the user if a specific user was searched for
            related_comments = Comment.query.filter_by(user_id = user.id).all()

    # Removes duplicates if there are any from combining the two lists together. Taken and modified from: https://stackoverflow.com/a/7961425
    comment_results = list(dict.fromkeys(comments + related_comments))

    return comment_results


def get_booking_results(search_query):
    """
    Handles search queries for bookings.
    
    Only displays results if the user is logged in and the booking belongs to their user ID.

    If no results found, returns an empty list.
    """
    booking_columns = [
        "booking_number",
        "quantity",
        "booking_date"
    ]

    filtered_events = []
    booking_results = []

    # Make sure user can only see the bookings if 1. They're logged in and 2. They booking belongs to their user id
    if current_user.is_authenticated:
        bookings = search_table(Booking, booking_columns, search_query)
        events = get_seminar_results(search_query)

        # From all events that match the query, filter it down to those with the same event_id as the booking, and then further filter it for only the users bookings
        if events:
            for event in events:
                filtered_events = Booking.query.filter_by(event_id = event.id, user_id = current_user.id).all()
                booking_results.extend(filtered_events)

        if bookings:
            for booking in bookings:
                if booking.user_id == current_user.id:
                    booking_results.append(booking)

        # Remove duplicates
        booking_results = list(dict.fromkeys(filtered_events + booking_results))
        
    return booking_results


def date_search(search_query):
    """Compares the search query against a dictionary of months to see if the input is a spelt out month as opposed to digits. If it is a spelt out month, turns it back into digits for compatibility with the database storage.

    Attempts to also see if there is a date and a year with the month. 

    Returns a "YYYY-MM-DD" if all are detected.
    Returns a "MM-DD" query if only month and day are detected.
    Returns "MM" if day and year not detected or search query only contains 1 word, otherwise returns the original search query.
    """
    months = {'january': '01', 'february': '02', 'march': '03', 'april':'04', 'may':'05', 'june':'06', 'july':'07', 'august':'08', 'september':'09', 'october':'10', 'november':'11', 'december':'12'}
    month = None
    day = None
    year = None

    # Split query into list and iterate it to see if there's potentially a day that goes with the month
    split_query = search_query.split()

    for word in split_query:
        for key, val in months.items():
                # If word is months key (e.g. spelt out month)
                if key.startswith(word):
                    month = val
                    search_query = val
                    break
        # If the split list is longer than 1, means maybe the date was included with it
        if len(split_query) > 1:
            # If word is a digit and between 1 and 31, maybe a date
            if word.isdigit() and word is not month:
                if 1 <= int(word) <= 31:
                    day = int(word)
                elif int(word) >= 2025:
                    year = int(word)

    # Check for day and year presence if we found a month and return those formatted values
    if month:
        if day and year:
            search_query = f"{year}-{month}-{day}"
        elif day:
            search_query = f"-{month}-{day}"

    return search_query


def time_search(search_query):
    """Attempts to match the search query against multiple different formats that the user may input.

    Covers:
    - AM/PM time: e.g. 01:30 am/pm or 1:30 am/pm or 01:30am/pm or 1:30am/pm
    - 24hr time: e.g. 13:30 or 01:30
    - 12hr time: e.g. 01:30 or 1:30

    If matches any of the formats, adds them to a list and returns it.
    """
    # Dfficult strptime formats to iterate through e.g. 1:30 pm/am
    am_pm_format = ["%I:%M %p",  "%-I:%M %p", "%I:%M%p", "%-I:%M%p"]
    parse_time = None

    time_queries = []

    # First search am/pm formats because they are definitive times
    for format in am_pm_format:
        try:
            parse_time = datetime.strptime(search_query, format).time()
            time_queries.append(parse_time.strftime("%H:%M"))
        except ValueError:
            # If error that means not am/pm times so put into 24 hour time format and get the opposite 12 hour time as well
            try:
                # 24 hour time
                parse_time = datetime.strptime(search_query, "%H:%M").time()
                time_queries.append(parse_time)

                # 12 hour time
                if parse_time.hour < 12:
                    # Pads the minutes with a zero if it is provided as a single digit time. E.g. 13:3 into 1:30
                    alternate_time = f"{parse_time.hour + 12}:{parse_time.minute:02}"
                    time_queries.append(alternate_time)
                elif parse_time.hour > 12:
                    # Pads the minutes and hours with a zero if it is provided as a single digit time. E.g. 1:3 into 01:30
                    alternate_time = f"{parse_time.hour - 12:02}:{parse_time.minute:02}"
                    time_queries.append(alternate_time)
            except:
                # If nothing, move on
                pass

    if time_queries:
        # Remove duplicates
        search_query = list(dict.fromkeys(time_queries))

    return search_query