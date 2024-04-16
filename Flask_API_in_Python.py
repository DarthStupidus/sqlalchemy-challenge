# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

# Import SQLAlchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask dependencies
from flask import Flask, jsonify

app = Flask(__name__)

# Database Setup

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup

# Create an app
app = Flask(__name__)

# Flask Routes

# Define the homepage route

@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define the /api/v1.0/precipitation route

# Return a json with precipitation data for the last 12 months

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date()
    one_year_ago = last_date - dt.timedelta(days=365)
    
    # Query the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_dict = {}
    for date, prcp in precipitation_data:
        precipitation_dict[date] = prcp
    
    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

# Define the /api/v1.0/stations route

# Give a JSON representation of all the stations in the database

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()

    station_data = [{"station": station, "name": name} for station, name in results]
    return jsonify(station_data)

# Define the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date()
    one_year_ago = last_date - dt.timedelta(days=365)
    
    # Query the temperature observations for the most active station for the last 12 months
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a list of dictionaries
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]
        
    # Return the JSON representation of the list
    return jsonify(temperature_list)

# Define the /api/v1.0/<start> and /api/v1.0/<start>/<end> routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    # Query temperature statistics based on start and end date
    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    
    # Convert the query results to a list of dictionaries
    temp_stats_list = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]
    
    # Return the JSON representation of the list
    return jsonify(temp_stats_list)

if __name__ == '__main__':
    app.run(debug=True)