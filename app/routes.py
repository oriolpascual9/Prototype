import flask
from flask import flash, session
from app.models import Class  # Updated to import the Class model from models.py
from flask import render_template, url_for, request, redirect
from app import db
from app import app

@app.route('/')
def home():  # Renamed to avoid conflicting with the other 'login' function
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']

    # Perform a query to find the class with the provided username
    class_data = Class.query.filter_by(name=username).first()  # Updated the query

    if class_data:
        # Save the class_id in the session
        session['class_id'] = class_data.id

        # Redirect to the class_data page for the specific class
        return redirect(url_for('class_data'))
    else:
        flash('Invalid username', 'error')
        return redirect(url_for('home'))


@app.route('/class_data')
def class_data():
    class_id = session.get('class_id')
    if not class_id:
        flash('Please log in first', 'error')
        return redirect(url_for('home'))

    # Fetch the class data using the class_id
    class_data = Class.query.get(class_id)

    return render_template('class_data.html', class_data=class_data)


@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    class_id = session.get('class_id')
    if not class_id:
        flash('Please log in first', 'error')
        return redirect(url_for('home'))

    # Fetch the class data using the class_id
    class_data = Class.query.get(class_id)

    # Update the class_data with the submitted vote
    transport_mode = int(request.form['transport_mode'])  # Convert the submitted value to an integer
    # Assuming you have a method called `add_vote` in your Votation model
    class_data.last_votation.add_vote(transport_mode)  # Updated to use last_votation

    # Commit the changes to the database
    db.session.commit()

    # Redirect to the class_data page
    return redirect(url_for('class_data'))
