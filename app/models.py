from app import db
from sqlalchemy.orm import relationship
import datetime

class Votation(db.Model):
    __tablename__ = "votation"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    voting_class = db.relationship('Class', back_populates='votations')
    npublic_transport = db.Column(db.Integer)
    ncar = db.Column(db.Integer)
    ncycling = db.Column(db.Integer)
    nwalking = db.Column(db.Integer)
    ncarpooling = db.Column(db.Integer)
    nothers = db.Column(db.Integer)

    def add_vote(self, transport_mode_index):
        self.results[transport_mode_index] += 1
        db.session.commit()


class Class(db.Model):
    __tablename__ = "class"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    nstudents = db.Column(db.Integer)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    school = relationship('School', back_populates='classes')
    last_votation_id = db.Column(db.Integer, db.ForeignKey('votation.id'))
    last_votation = relationship('Votation', uselist=False, post_update=True)
    votations = relationship('Votation', back_populates='voting_class')

    votes = db.relationship('Vote', back_populates='class_rel')

    def add_vote(self, transport_mode):
        new_vote = Vote(transport_mode=transport_mode, class_id=self.id)
        db.session.add(new_vote)
        db.session.commit()

class School(db.Model):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))
    league = relationship('League', back_populates='schools')
    classes = relationship('Class', back_populates='school')

class League(db.Model):
    __tablename__ = 'league'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    #start_time = db.Column(db.DateTime)
    #end_time = db.Column(db.DateTime)
    schools = relationship('School', back_populates='league')

    def add_league(self, league_name, start_time, end_time):
        new_vote = League(league_name, start_time, end_time, class_id=self.id)
        db.session.add(new_vote)
        db.session.commit()
