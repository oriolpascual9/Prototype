from app import db
from sqlalchemy.orm import relationship

class Votation(db.Model):
	__tablename__ = "votation"

	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime)
	voting_class = relationship('Class')
	results = db.Column(db.ARRAY(db.Integer)) #


class Class(db.Model):

	__tablename__ = "class"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	nstudents = db.Column(db.Integer)
	school = relationship('School')

class School(db.Model):
	__tablename__ = 'schools'

	id = db.Column(db.Integer,primary_key=True)
	league = relationship('League')

class League(db.Model):

	__tablename__ = 'league'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	start_time = db.Column(db.DateTime)
	end_time = db.Column(db.DateTime)

