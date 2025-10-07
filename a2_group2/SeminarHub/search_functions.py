"""
This file contains helper functions that enable the search bar to work.
"""

from .models import Event, Booking, Comment, User
from flask_login import login_required, current_user
from sqlalchemy import or_

def search_table(model, columns, search_query):
    """
    Parses through each column of a given database table using pythons built in getattr() method, attempts to match a case insensitive (ilike) query and then returns all rows that match that query from the table.

    Taken and modified from: https://stackoverflow.com/a/57192587

    Explanation:
    getattr(object, attribute) = where the object is the table name and the attribute is the column name. Returns the value of a name attribute of an object (e.g. returns the value of Event.title).

    or_ = Essentially an SQL OR statement.

    * = Unpacks a List and passes each element in the list as seperate arguments into the or_ statment.
    """
    sql_queries = or_(*[getattr(model, col).ilike(f'%{search_query}%') for col in columns])

    final_list = model.query.filter(sql_queries).all()
    
    return final_list


def get_page_results(search_query):
    """
    Creates multiple dictionaries that have key words that might be related to distinct pages in the web application.

    If the search query is one of these key words, return a list containing the dictionary.

    If no key words detected, return an empty list.
    """

    # Page dictionaries
    bookings = {'name': 'My Bookings', 'link':'main.booking', 'searchable_words':['book', 'booking', 'my booking', 'my bookings', 'bookings']}
    user = {'name': 'Profile', 'link':'user.seminars', 'searchable_words':['profile', 'my profile', 'my account', 'account', 'my seminars']}
    create = {'name': 'Create Seminar', 'link': 'main.create', 'searchable_words':['create', 'create seminar']}

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
    # Next check for seminars in database
    seminar_columns = [
        "title",
        "description",
        "category",
        "location",
        "status",
        "speaker",
        "speaker_bio"
    ]

    seminar_results = search_table(Event, seminar_columns, search_query)

    return seminar_results


def get_comment_results(search_query):
    """
    Uses the search_table() function to query each column within the Comment and User table and return results as a list if they match the search query.

    Handles searches for comment text and users names.

    If no results found, returns an empty list.
    """
    comment_columns = [
        "text"
    ]
    user_columns = [
        "first_name",
        "last_name"
    ]

    # Get users based on first or last name only if searched for
    user_results = search_table(User, user_columns, search_query)
    # Get comments based on comment text
    comments = search_table(Comment, comment_columns, search_query)

    # Initialise empty list
    related_comments = []

    if user_results:
        for user in user_results:
            # Get comments that are made by the user if a specific user was searched for
            related_comments = Comment.query.filter_by(user_id = user.id).all()

    # Removes duplicates if there are any from combining the two lists together
    comment_results = list(dict.fromkeys(comments + related_comments))

    return comment_results


def get_booking_results(search_query):
    """
    Handles search queries for a booking number.
    
    Only displays results if the user is logged in and if their ID matches the foreign key user_id in the Booking table.

    If no results found, returns an empty list.
    """
    booking_results = []

    # If user is logged in retrieve their bookings if searched for
    if current_user.is_authenticated:

        booking_results = Booking.query.filter(Booking.user_id == current_user.id, Booking.booking_number.ilike(f'%{search_query}%')).all()
        
    return booking_results