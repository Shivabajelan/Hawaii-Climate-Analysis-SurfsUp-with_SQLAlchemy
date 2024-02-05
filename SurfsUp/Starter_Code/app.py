# Dependencies
import numpy as np
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# assign the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/start/MMDDYYYY<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/start/end/MMDDYYYY/MMDDYYYY<br/>"
        f"NOTICE:<br/>"
        f"Please input the query date in the string format as (MMDDYYYY),<br/>"
        f"and the start date should not be later than 2017-08-23."
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return a list of precipitation data including the date and precipitation score of each row"""
    # Query all dates and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitations
    all_precipitations = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitations.append(precipitation_dict)

    return jsonify(all_precipitations)


@app.route("/api/v1.0/stations")
def stations():
    
    """Return a list of all stations' name from the dataset"""
    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    
    """Return a list of the dates and temperature observations of the most-active station for the previous year of data"""
    # Calculate the date one year from the last date in data set. (first we need to convert the most_recent_date to a datetime object)
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the dates and temperature observations of the most-active station for the previous year of data
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    session.close()

    # Convert list of tuples into normal list
    precipitation_per_date = list(np.ravel(results))

    return jsonify(precipitation_per_date)




@app.route("/api/v1.0/start/<start_date>")
def temperature_aggregation_by_start_date(start_date):
    """calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date
    that start date matches the path variable supplied by the user, or a 404 if not."""
    # Convert the date type from string to datetime object
    sanitised = dt.datetime.strptime(start_date, "%m%d%Y" )

    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date>= sanitised).\
        group_by(Measurement.date).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)


@app.route("/api/v1.0/start/end/<start>/<end>") 
def temperature_aggregation_by_start_and_end_date(start, end):

    # Convert the date type from string to datetime object
    sanitised_start = dt.datetime.strptime(start, "%m%d%Y" )
    sanitised_end = dt.datetime.strptime(end, "%m%d%Y" )

    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date>= sanitised_start).filter(Measurement.date<= sanitised_end).\
        group_by(Measurement.date).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_tobs_interval = list(np.ravel(results))

    return jsonify(all_tobs_interval)


if __name__ == "__main__":
    app.run(debug=True)

