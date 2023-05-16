from flask import flash, session, render_template, redirect, url_for, request
from app.models import Class, Votation
from app import db, app
import datetime

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
    class_id = session.get('class_id')
    if not class_id:
        flash('Please log in first', 'error')
        return redirect(url_for('home'))

    today = datetime.datetime.now(datetime.timezone.utc).date()
    transport_mode = request.form['transport_mode']
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
