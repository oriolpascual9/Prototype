import flask
from flask import flash, session
from app.models import Class, Votation  # Updated to import the Class model from models.py
from flask import render_template, url_for, request, redirect
from app import db
from app import app
import datetime

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
    # today = datetime(2023, 5, 15, 11, 18, 23, 628854)
    today = datetime.datetime.now(datetime.timezone.utc).date()
    transport_mode = request.form['transport_mode']
    votation_data = db.session.query(Votation).filter(Votation.date==today and Votation.class_id==class_id)

    if not votation_data.first():
        todays_votation = Votation(date = today, class_id= class_id, \
            nwalking = 0, ncycling = 0, ncar = 0, npublic_transport = 0, ncarpooling = 0, nothers = 0)
        db.session.add(todays_votation)
        db.session.commit()

        votation_data = db.session.query(Votation).filter(Votation.date==today and Votation.class_id==class_id)

    record = votation_data.first() #should only be one
    if transport_mode == 'foot':
        record.nwalking += 1

    elif transport_mode == 'bike':
        record.ncycling += 1
    
    elif transport_mode == 'car':
        record.ncar += 1
    
    elif transport_mode == 'bus':
        record.npublic_transport += 1
    
    elif transport_mode == 'carpooling':
        record.ncarpooling += 1
    
    elif transport_mode == 'other':
        record.nothers += 1
    
    # Update the class_data with the submitted vote
    db.session.commit()
    total_transport = record.nwalking +  record.ncycling + record.ncar + record.npublic_transport + record.ncarpooling + record.nothers
    transport_list = [record.nwalking, record.ncycling, record.ncar, record.npublic_transport, record.ncarpooling, record.nothers]
    transport_list = list(map(lambda x: x*100/total_transport, transport_list))

    import sys
    print(transport_list, file=sys.stderr)

    # Redirect to the class_data page
    return render_template('class_data.html', transport_list = transport_list)
