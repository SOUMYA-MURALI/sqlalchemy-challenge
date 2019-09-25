# Dependencies and setup
import numpy as np
import pandas as pd
from datetime import datetime 
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
# "falsk" is the framework while "Flask" is the python class data type
# Used Flask jsonify to convert your API data into a valid JSON response object

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Save references to the measurement and station tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup
#Flask constructor takes the name of current module (__name__) as argument.
# The route() function of the Flask class is a decorator, which tells the application which URL should call the associated function.
# create an instance of the Flask class for our web app.

app = Flask(__name__)
# Flask will call functions


# Querying the latest year date 
# By using order_by in descending order
latest_date = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
# np.ravel converting list of list into a single list
latest_date = list(np.ravel(latest_date))[0]
latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')

# getting year from latest year date
latest_year = int(dt.datetime.strftime(latest_date, '%Y'))
# getting month from latest year date
latest_month = int(dt.datetime.strftime(latest_date, '%m'))
# getting day from latest year date
latest_day = int(dt.datetime.strftime(latest_date, '%d'))

# Querying the last year date
year_before = dt.date(latest_year, latest_month, latest_day) - dt.timedelta(days=365)
year_before = dt.datetime.strftime(year_before, '%Y-%m-%d')


# Flask Routes
# created Flask Routes

@app.route("/")
def home():
    # list all routes that are available
    # list hyperlinks for the routes
    # print the data available
    return (f"<H2>Welcome to the Hawaii Climate Analysis API!</br></H2>"
            f"<H3>Available Routes:</H3>"
            f"<H4>Static Routes:</H4>"
            f"/api/v1.0/stations ~~~~~~~ a list of all weather observation stations<br/>"
            f"/api/v1.0/precipitaton ~~~ preceipitation data for last year<br/>"
            f"/api/v1.0/temperature ~~~~ temperature data for last year<br/>"
            f"<br/>"
            f"<H4>Dynamic Routes:</H4>"
            f"/api/v1.0/datesearch/2017-06-09~~~~~~~~~~~ low, high, and average temp for dates greater than and equal to the startDate [format (yyyy-mm-dd)] <br/>"
            f"/api/v1.0/datesearch/2017-06-09/2017-06-15 ~~ low, high, and average temp for dates between given startDate and endDate [format (yyyy-mm-dd)] <br/>"
            f"<br/>"
            f"<br/>"
            f"<H4>Hyper Links:</H4>"
            f"<a href='http://127.0.0.1:5000/api/v1.0/stations'>List of weather observation stations</a><br/>"
            f"<a href='http://127.0.0.1:5000/api/v1.0/precipitaton'>Precipitation Data</a><br/>"
            f"<a href='http://127.0.0.1:5000/api/v1.0/temperature'>Temperature Data</a><br/>"
            f"<a href='http://127.0.0.1:5000/api/v1.0/datesearch/2017-06-09'>Temperature Data from Start Date</a><br/>"
            f"<a href='http://127.0.0.1:5000/api/v1.0/datesearch/2017-06-09/2017-06-15'>Temperature Data between Start Date and End Date</a><br/>"
            f"<br>"
            f"<br>~~~~~~~~~~~~~~~~~~~~~~~~~~ Data available from 2010-01-01 to 2017-08-23 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            
@app.route("/api/v1.0/stations")
def stations():
    # list all weather observation stations
    # querying name from table Station
    results = session.query(Station.name).all()
    # using ravel to convert list of list into a single list
    all_stations = list(np.ravel(results))
    # jsonifying all_stations
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    # precipitation data from 2016-08-24 t0 2017-08-23 with station by using filter
    # year_before: 2016-08-23
    # "order_by" is used to get data by date in ascending order

    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > year_before)
                      .order_by(Measurement.date)
                      .all())
    # appending precipitation dictionaries "prcp_dict" to the list "prcp_list"
    prcp_list = []
    for result in results:
        prcp_dict = {result.date: result.prcp, "Station": result.station}
        prcp_list.append(prcp_dict)
    # jsonifying prcp_list
    return jsonify(prcp_list)

@app.route("/api/v1.0/temperature")
def temperature():
    # temperature data from 2016-08-24 t0 2017-08-23 with station by using filter
     # "order_by" is used to get data by date in ascending order
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > year_before)
                      .order_by(Measurement.date)
                      .all())
    # appending temperature dictionaries "temp_dict" to the list "temp_list"
    temp_list = []
    for result in results:
        temp_dict = {result.date: result.tobs, "Station": result.station}
        temp_list.append(temp_dict)
    # jsonifying the temp_list
    return jsonify(temp_list)

@app.route("/api/v1.0/datesearch/<startDate>")
def start(startDate):
    # Temperature data available from start date to 2017-08-23 by using filter 
    # group_by date
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    # appending dictionaries with "Date","TMIN","TAVG","TMAX" to the list "date_list"
    date_list = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["TMIN"] = result[1]
        date_dict["TAVG"] = result[2]
        date_dict["TMAX"] = result[3]
        date_list.append(date_dict)
    # jsonifying the date_list    
    return jsonify(date_list)

@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    # Temperature data available between start date and end date
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # filter is used to get start date and end date
    # group_by date
    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    # appending dictionaries with "Date","TMIN","TAVG","TMAX" to the list "date_list"
    date_list = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["TMIN"] = result[1]
        date_dict["TAVG"] = result[2]
        date_dict["TMAX"] = result[3]
        date_list.append(date_dict)
     # jsonifying the date_list   
    return jsonify(date_list)


# Python assigns the name "__main__" to the script when the script is executed.
#   "__name__" is a variable automatically set in an executing python program
#If you import your module from another program, __name__ will be set to the name of the module
# Here program run directly    
#If you run your program directly, __name__ will be set to __main__


if __name__ == "__main__":
    #print ("I am being run directly")
    app.run(debug=True)
#else:
    #print ("I am being imported")
