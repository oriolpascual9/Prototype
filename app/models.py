from app import db

class Class(db.Model):

	__tablename__ = "class"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	nstudents = db.Column(db.Integer)

class School(db.Model):
	__tablename__ = 'schools'

	id = db.Column(db.Integer,primary_key=True)