# autograding-of-cs-courses

5th Semester project for SE subject offered by UET, Lahore.

To run:

Activate the virtual environment (it might install some packages)

    pipenv shell

Install Flask, Flask-SQLAlchemy.

    pipenv install flask, flask-sqlalchemy

Before running, you must initiate the database by first activating the virtual environment and then execute python shell by the following command:

    drive:/path> python

Then, enter the following commands:

    > from app import db
    > db.create_all()

After this, you can exit the terminal using `exit()`
and then run the following command to run the localhost.

    python app.py

Make sure the virtual environment is activated