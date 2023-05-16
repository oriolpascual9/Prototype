from flask import flash, session, render_template, redirect, url_for, request, jsonify
from app.models import Class, Votation
from app import db, app
import datetime
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
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

    votation_data = Votation.query.filter(Votation.class_id == class_id).first()
    transport_list = []
    if votation_data:
        total_transport = votation_data.nwalking + votation_data.ncycling + votation_data.ncar + \
                          votation_data.npublic_transport + votation_data.ncarpooling + votation_data.nothers
        if total_transport != 0:
            transport_list = [votation_data.nwalking, votation_data.ncycling, votation_data.ncar,
                              votation_data.npublic_transport, votation_data.ncarpooling, votation_data.nothers]
            transport_list = [round((x * 100) / total_transport, 2) for x in transport_list]

    return render_template('class_data.html', class_data=class_data, transport_list=transport_list)

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

        if not votation_data:
            votation_data = Votation(date=today, class_id=class_id, nwalking=0, ncycling=0, ncar=0,
                                     npublic_transport=0, ncarpooling=0, nothers=0)
            db.session.add(votation_data)
            db.session.commit()

        if transport_mode == 'foot':
            votation_data.nwalking += 1
        elif transport_mode == 'bike':
            votation_data.ncycling += 1
        elif transport_mode == 'car':
            votation_data.ncar += 1
        elif transport_mode == 'bus':
            votation_data.npublic_transport += 1
        elif transport_mode == 'carpooling':
            votation_data.ncarpooling += 1
        elif transport_mode == 'other':
            votation_data.nothers += 1

        db.session.commit()

        return redirect(url_for('class_data'))

    except Exception as e:
        logging.exception("Exception occurred")
        print(e)  # printing out the exception message
        return "An error occurred while submitting vote", 500  # return a user-friendly error message

from flask import jsonify

@app.route('/get_vote_data', methods=['GET'])
def get_vote_data():
    try:
        class_id = session.get('class_id')
        if not class_id:
            return jsonify({'error': 'Please log in first'}), 401

        today = datetime.datetime.now(datetime.timezone.utc).date()
        votation_data = Votation.query.filter(Votation.date == today, Votation.class_id == class_id).first()

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
