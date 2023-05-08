import flask
from flask import render_template,url_for,request,redirect
from app import db
from app import app

@app.route('/')
def login():
    return render_template('login.html')
