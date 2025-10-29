from flask import Flask, request, render_template, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from datetime import datetime

db = SQLAlchemy()

def create_app():

   app = Flask(__name__)  
   # Debug false on production version
   app.debug = False
   # Secret key randomised from Python 'secrets' package. Would not be hardcoded in a real application
   app.secret_key = '3d34ba27378f990f46d1f9b698791c0a13d2cd389077e155'
   # set the app configuration data 
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seminarhub.sqlite'
   # initialise db with flask app
   db.init_app(app)

   Bootstrap5(app)
   
   # initialise the login manager
   login_manager = LoginManager()
   
   # Set the name of the login function that lets user login - auth.login
   login_manager.login_view = 'auth.login'
   login_manager.init_app(app)

   # create a user loader function takes userid and returns User
   # Importing inside the create_app function avoids circular references
   from .models import User
   @login_manager.user_loader
   def load_user(user_id):
      return db.session.scalar(db.select(User).where(User.id==user_id))

   # Import main blueprint
   from .main import views
   app.register_blueprint(views.main_bp)
   # Import authentication blueprint
   from .auth import auth
   app.register_blueprint(auth.auth_bp)
   # Import event blueprint
   from .event import event
   app.register_blueprint(event.event_bp)
   # Import booking blueprint
   from .booking import booking
   app.register_blueprint(booking.booking_bp)
   # Import user blueprint
   from .user import user
   app.register_blueprint(user.user_bp)

   # Error handling for errors 404 and 500
   @app.errorhandler(404)
   def page_not_found(error):
      # Render 404 template
      return render_template('404.html', heading = 'Page Missing | '), 404

   @app.errorhandler(500)
   def internal_error(error):
      # Render 500 tempalte
      return render_template('500.html', heading = 'Server Error | '), 500
   
   # Last seen helper
   @app.before_request
   def before():
      # If logged in set the last seen datetime object and add to database
      if current_user.is_authenticated:
         current_user.last_seen = datetime.now()
         db.session.commit()
   
   return app