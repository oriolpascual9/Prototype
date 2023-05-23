from flask import flash, session, render_template, redirect, url_for, request, jsonify
from app.models import Class, Votation
from app import db, app
import datetime
import logging
import sys
from flask import session


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']

    # if the username is "admin", redirect to dashboard
    if username == 'admin':
        session['username'] = username
        return redirect(url_for('dashboard'))

    class_data = Class.query.filter_by(name=username).first()

    if class_data:
        session['class_id'] = class_data.id
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

    class_data = Class.query.get(class_id)
    class_name = class_data.name if class_data else ''
    
    # Get the selected date from the request's query parameters
    selected_date = request.args.get('date-filter')
    if selected_date:
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date = datetime.datetime.now(datetime.timezone.utc).date()

    votation_data = Votation.query.filter(Votation.date == selected_date, Votation.class_id == class_id).first()

    no_data = False
    transport_list = []
    score = '0'
    if votation_data:
        total_transport = votation_data.nwalking + votation_data.ncycling + votation_data.ncar + \
                          votation_data.npublic_transport + votation_data.ncarpooling + votation_data.nothers
        if total_transport != 0:
            transport_list = [votation_data.nwalking, votation_data.ncycling, votation_data.ncar,
                              votation_data.npublic_transport, votation_data.ncarpooling, votation_data.nothers]
        
        score = str(votation_data.score)
    else:
        no_data = True

    return render_template('class_data.html', class_data=class_data, transport_list=transport_list, score=score, selected_date=selected_date, class_name=class_name, no_data=no_data)

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    try:
        class_id = session.get('class_id')
        if not class_id:
            flash('Please log in first', 'error')
            return redirect(url_for('home'))

        today = datetime.datetime.now(datetime.timezone.utc).date()
        transport_mode = request.form.get('transport_mode')  # change this line

        # Check if transport_mode is not None
        if not transport_mode:
            flash('Transport mode not provided', 'error')
            return redirect(url_for('class_data'))
        
        votation_data = Votation.query.filter(Votation.date == today, Votation.class_id == class_id).first()

        # When there's no votation data for today, create it
        if not votation_data:
            votation_data = Votation(date=today, class_id=class_id, nwalking=0, ncycling=0, ncar=0,
                                     npublic_transport=0, ncarpooling=0, nothers=0, score=0)
            db.session.add(votation_data)

        if transport_mode == 'foot':
            votation_data.nwalking += 1
            votation_data.score += 25
        elif transport_mode == 'bike':
            votation_data.ncycling += 1
            votation_data.score += 25
        elif transport_mode == 'car':
            votation_data.ncar += 1
            votation_data.score += 5
        elif transport_mode == 'bus':
            votation_data.npublic_transport += 1
            votation_data.score += 15
        elif transport_mode == 'carpooling':
            votation_data.ncarpooling += 1
            votation_data.score += 10
        elif transport_mode == 'other':
            votation_data.nothers += 1
            votation_data.score += 5

        db.session.commit()

        return redirect(url_for('class_data'))

    except Exception as e:
        logging.exception("Exception occurred")
        print(e)  # printing out the exception message
        return "An error occurred while submitting vote", 500  # return a user-friendly error message

@app.route('/get_vote_data', methods=['GET'])
def get_vote_data():
    try:
        class_id = session.get('class_id')
        if not class_id:
            return jsonify({'error': 'Please log in first'}), 401

        date = request.args.get('date')
        selected_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        votation_data = Votation.query.filter(Votation.date == selected_date, Votation.class_id == class_id).first()

        if not votation_data:
            return jsonify({'error': 'No voting data available'}), 404
        
        data = {
            'foot': votation_data.nwalking,
            'bike': votation_data.ncycling,
            'car': votation_data.ncar,
            'bus': votation_data.npublic_transport,
            'carpooling': votation_data.ncarpooling,
            'other': votation_data.nothers,
        }

        return jsonify(data)

    except Exception as e:
        logging.exception("Exception occurred")
        return jsonify({'error': 'An error occurred while getting vote data'}), 500

@app.route('/delete_last_vote', methods=['POST'])
def delete_last_vote():
    try:
        class_id = session.get('class_id')
        if not class_id:
            return jsonify({'error': 'Please log in first'}), 401

        today = datetime.datetime.now(datetime.timezone.utc).date()

        # Find the last vote for the current date and class_id
        votation_data = Votation.query.filter(
            Votation.date == today, Votation.class_id == class_id
        ).order_by(Votation.id.desc()).first()

        if not votation_data:
            return jsonify({'error': 'No vote to delete'}), 404

        # Decrement the count and score based on the transport mode of the last vote
        if votation_data.nothers > 0:
            votation_data.nothers -= 1
            votation_data.score -= 5
        elif votation_data.ncarpooling > 0:
            votation_data.ncarpooling -= 1
            votation_data.score -= 10
        elif votation_data.npublic_transport > 0:
            votation_data.npublic_transport -= 1
            votation_data.score -= 15
        elif votation_data.ncar > 0:
            votation_data.ncar -= 1
            votation_data.score -= 5
        elif votation_data.ncycling > 0:
            votation_data.ncycling -= 1
            votation_data.score -= 25
        elif votation_data.nwalking > 0:
            votation_data.nwalking -= 1
            votation_data.score -= 25

        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        logging.exception("Exception occurred")
        return jsonify({'error': 'An error occurred while deleting the last vote'}), 500
@app.route('/register', methods=['POST'])
def register():
    classname = request.form['classname']
    nstudents = int(request.form['nstudents'])
    school_id = int(request.form['school'])
    new_class = Class(name=classname, nstudents=nstudents, school_id=school_id)
    db.session.add(new_class)
    db.session.commit()
    return redirect('/')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))

    # retrieve all the classes from the database
    classes = Class.query.all()

    # logic for filtering data and creating pie chart goes here

    return render_template('dashboard.html', classes=classes)



