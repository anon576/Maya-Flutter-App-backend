from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import pytz
from sqlalchemy import Date
indian_timezone = pytz.timezone('Asia/Kolkata')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maya.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "User"
    uid = db.Column(db.Integer,autoincrement=True,nullable=False,primary_key = True)
    password = db.Column(db.String)
    firstName = db.Column(db.String,nullable=False)
    lastName = db.Column(db.String,nullable=False)
    email = db.Column(db.String,nullable=False)
    mobileno = db.Column(db.String,nullable=True)
    dob =  db.Column(db.String)
    partner = db.Column(db.String)
    cycleRange = db.Column(db.Integer)
    periodRange = db.Column(db.Integer)
    cycleRegular = db.Column(db.String)
    discomfort = db.Column(db.String)
    disorder = db.Column(db.String)
    sleep = db.Column(db.String)
    periodStartDate = db.Column(db.String)
    periodEndDate=db.Column(db.String)
    cycleStartDate = db.Column(db.String)
    cycleEndDate=db.Column(db.String)
    
    
    

class Partner(db.Model):
    __tablename__ = "Partner"
    pid = db.Column(db.Integer,autoincrement=True,nullable=False,primary_key = True)
    password = db.Column(db.String)
    uid = db.Column(db.Integer,db.ForeignKey('User.uid'),nullable=False)
    firstName = db.Column(db.String,nullable=False)
    lastName = db.Column(db.String,nullable=False)
    email = db.Column(db.String,nullable=False)
    mobileno = db.Column(db.String,nullable=True)


class Cycle(db.Model):
    __tablename__ = "Cycle"
    cID = db.Column(db.Integer,autoincrement=True,nullable=False,primary_key=True)
    uid = db.Column(db.Integer,db.ForeignKey('User.uid'),nullable=False)
    startdate = db.Column(db.DateTime)
    enddate = db.Column(db.DateTime)
    range = db.Column(db.Integer)



class Period(db.Model):
    __tablename__ = "Period"
    pID = db.Column(db.Integer,autoincrement=True,nullable=False,primary_key=True)
    uid = db.Column(db.Integer,db.ForeignKey('User.uid'),nullable=False)
    cID = db.Column(db.Integer,db.ForeignKey('Cycle.cID'),nullable=False)
    startdate = db.Column(db.DateTime)
    enddate = db.Column(db.DateTime)
    range = db.Column(db.Integer)



class Days(db.Model):
    __tablename__ = "Days"
    dID = db.Column(db.Integer,autoincrement=True,nullable=False,primary_key=True)
    uid = db.Column(db.Integer,db.ForeignKey('Cycle.cID'),nullable=False)
    day = db.Column(db.Integer)
    date = db.Column(db.String)
    today = db.Column(db.String)
    symptons = db.Column(db.String)
    description = db.Column(db.String)
    cycleUpdate1 = db.Column(db.String,nullable = False)
    cycleUpdate2 = db.Column(db.String,nullable = False)
    ovdays = db.Column(db.String)
    nextPeriods = db.Column(db.String)


class Notes(db.Model):
    __tablename__ = "Notes"
    nID = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.uid'), nullable=False)
    date = db.Column(db.String)  # Use Date type instead of DateTime
    note = db.Column(db.String)


class Symptons(db.Model):
    __tablename__ = "Symptons"
    nID = db.Column(db.Integer,autoincrement=True,nullable=False,primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.uid'), nullable=False)
    date = db.Column(db.String)
    symptons = db.Column(db.String)


class Sleep(db.Model):
    __tablename__ = "Sleep"
    nID = db.Column(db.Integer,autoincrement=True,nullable=False,primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.uid'), nullable=False)
    date = db.Column(db.String)
    sleep = db.Column(db.String)



