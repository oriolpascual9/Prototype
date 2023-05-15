import flask
from flask import flash, session
from app.models import Class, Votation  # Updated to import the Class model from models.py
from flask import render_template, url_for, request, redirect
from app import db
from app import app
from datetime import date, datetime

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

    votation_data = session.query(Votation).filter(class_id)
    today = datetime(2023, 5, 15, 11, 18, 23, 628854)
    created = False
    for vote in votation_data:
        if vote.date == today:
            created = True
            todays_votation = vote

    if not created:
        todays_votation = Votation(date = today, class_id= class_id)

    transport_mode = request.form['transport_mode']

    if transport_mode == 1:
        print("Woooorking")
        todays_votation.nwalking += 1

    elif transport_mode == 2:
        todays_votation.ncycling += 1

    # Update the class_data with the submitted vote

    # Redirect to the class_data page
    return redirect(url_for('class_data'))
