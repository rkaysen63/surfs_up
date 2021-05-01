# Import dependencies and assign an alias.
import datetime as dt
import numpy as np
import pandas as pd

# Import dependencies for SQLAlchemy to access SQLite database
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import the dependencies required for Flask. 
from flask import Flask, jsonify

# Set up database engine to access and query SQLite database for the Flask application.
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into the classes
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Session link from Python to database
session = Session(engine)

# Define Flask app
app = Flask(__name__)

# Define root, or welcome route
@app.route("/")

# Create additional routes
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

# Create the precipitation route
@app.route("/api/v1.0/precipitation")

# Create the precipitation function.
def precipitation():
    # Calculate the date one year before the most recent date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query to get date and precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # Use jsonify() to format results into a JSON structured file.
    precip = {date: prcp for date, prcp in precipitation}

    return jsonify(precip)

# Create the stations route.
@app.route("/api/v1.0/stations")

# Create the stations function.
def stations():  

    # Query to get all of the stations in the database.
    results = session.query(Station.station).all()

    # Unravel results into a one-dimensional array and convert results into a list.
    stations = list(np.ravel(results))

    # Use jsonify() to format results into a JSON structured file.
    return jsonify(stations=stations)
    
# Create the temperature observations (tobs) route.
@app.route("/api/v1.0/tobs")

# Create the monthly temperature function.
def temp_monthly():

    # Calculate the date one year before the most recent date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)  

    # Query primary station to get all temp observations from the previous year.
    results = session.query(Measurement.tobs).\
	    filter(Measurement.station == 'USC00519281').\
	    filter(Measurement.date >= prev_year).all()

    # Unravel results into a one-dimensional array and convert results into a list.
    temps = list(np.ravel(results))

    # Use jsonify() to format results into a JSON structured file.
    return jsonify(temps=temps)

# Statistics Route - create starting and ending routes.
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

# Create temperature stats function with start and end parameters.
def stats(start=None, end=None):
    
    # Create a query to select the minimum, average and maximum temperatures from database
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Calculate the temp min, avg, max w start and end dates.
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)