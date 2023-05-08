from app import db
from sqlalchemy.orm import relationship

class Votation(db.Model):
    __tablename__ = "votation"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    voting_class = relationship('Class', back_populates='votations')
    results = db.Column(db.ARRAY(db.Integer))

    def add_vote(self, transport_mode_index):
        self.results[transport_mode_index] += 1

class Class(db.Model):
    __tablename__ = "class"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    nstudents = db.Column(db.Integer)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    school = relationship('School', back_populates='classes')
    last_votation_id = db.Column(db.Integer, db.ForeignKey('votation.id'))
    last_votation = relationship('Votation', uselist=False, post_update=True)
    avg_results = db.Column(db.ARRAY(db.Integer))
    votations = relationship('Votation', back_populates='voting_class')

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
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    schools = relationship('School', back_populates='league')
