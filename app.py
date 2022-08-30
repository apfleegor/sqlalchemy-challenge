# import
from flask import Flask, jsonify

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# setup Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# setup Flask
app = Flask(__name__)


# index route
@app.route("/")
def home():
    return(
        f"Welcome to the Homework Homepage!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start-date<br/>"
        f"/api/v1.0/start-date/end-date"
    )


# precipitation route
@app.route("/api/v1.0/precipitation")
def precip(): #@TODO
    # create session
    session = Session(engine)

    # convert the query results to a dictionary using date as the key and prcp
    # as the value
    # copy from jupyter notebook
    recent_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent = dt.datetime.strptime(recent_str, '%Y-%m-%d')
    one_year = most_recent - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year).all()
    
    # return the json representation of your dictionary
    final_results = []
    for date, precip in results:
        final_results.append({date: precip})

    session.close()
    return jsonify(final_results)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    # create session
    session = Session(engine)

    # return a JSON list of stations from the dataset
    results = session.query(Station.station).all()

    session.close()

    # convert list of tuples
    final_results = list(np.ravel(results))

    return jsonify(final_results)

# tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # create session
    session = Session(engine)

    # Query the dates and temperature observations of the most active station
    # for the previous year of data.

    # copy code from jupyter notebook
    recent_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent = dt.datetime.strptime(recent_str, '%Y-%m-%d')
    one_year = most_recent - dt.timedelta(days=365)

    active = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc())
    most_active_id = active[0][0]
    active_year = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_id).\
        filter(Measurement.date > one_year).all()
    
    # Return a JSON list of temperature observations (TOBS) for the previous 
    # year.
    results_dict = []
    for date, temp in active_year:
        tob_dict = {}
        tob_dict['date'] = date
        tob_dict['tobs'] = temp
        results_dict.append(tob_dict)

    session.close()

    return jsonify(results_dict)

# start range route
@app.route("/api/v1.0/<start>")
def start(start):
    # create session
    session = Session(engine)

    # calculate TMIN, TAVG, and TMAX for all dates 
    # greater than or equal to the start date.
    start_obs = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Return a JSON list of the min, avg, max temp 
    # for a given start range.
    results = [
        {'min': start_obs[0][0]},
        {'max': start_obs[0][1]},
        {'average': start_obs[0][2]}
    ]
    
    session.close()

    return jsonify(results)

# start plus end range route
@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    # create session
    session = Session(engine)

    # calculate the TMIN, TAVG, and TMAX
    # for dates from start through end date (inclusive)
    start_end_obs = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Return a JSON list of the min, avg, max temp 
    # for a given start-end range.
    results = [
        {'min': start_end_obs[0][0]},
        {'max': start_end_obs[0][1]},
        {'average': start_end_obs[0][2]}
    ]
   
    session.close()

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
