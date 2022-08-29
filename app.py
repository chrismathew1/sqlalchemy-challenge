import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station


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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    '''
    Convert the query results to a dictionary using date as the key and prcp as the value.
    Return the JSON representation of your dictionary.
    '''
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    
    session.close()


    precipitation_all = {}

    for date, prcp in results:
        precipitation_all.update({date:prcp})
    


    return jsonify(precipitation_all)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    '''
    Return a JSON list of stations from the dataset.
    '''
    results = session.query(Station.station).all()

    session.close()
    
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    '''
    Query the dates and temperature observations of the most active station for the last year of data.
    Return a JSON list of temperature observations (TOBS) for the previous year.
    '''
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    most_active = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    results = session.query(Measurement.tobs).filter(Measurement.station==most_active[0][0]).filter(Measurement.date >= year_ago).all()


    session.close()

    all_temps = list(np.ravel(results))

    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    start_temp = list(np.ravel(results))

    return jsonify(start_temp)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    start_end_temp = list(np.ravel(results))

    return jsonify(start_end_temp)




if __name__ == '__main__':
    app.run(debug=True)
