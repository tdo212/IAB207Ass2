from SeminarHub import create_app

if __name__ == '__main__':
    app = create_app()
    app.run()

''' 
# this can be used later to initialise our database!
from SeminarHub import create_app, db
from create_db import create_database

app = create_app()

# initialise database with dummy data.
with app.app_context():
    create_database(app)

if __name__ == '__main__':
    app.run(debug=True)
'''
