# Import the dependencies.
import datetime as dt
import numpy as np
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
Base.prepare(engine)


# Save references to each table
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
# Setup and query structure are partly borrowed from Drew's speed run
#################################################

@app.route("/")
def welcome():
   #List all available API routes
   return(
       f"Available routes:<br/>"
       f"/api/v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/>"
       f"/api/v1.0/start<br/>"
       f"/api/v1.0/start/end"
   )


@app.route("/api/v1.0/precipitation")
def precipitation():

   #Query the precipitation data
   end_date = dt.date(2017,8,23)
   start_date = dt.date(2016,8,23)
  
   precipitation_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date)

   session.close()

   # Create a dictionary of precipitation data and append to a list
   precipitation_data = []
   for date, prcp in precipitation_results:
       precipitation_dict = {}
       precipitation_dict["date"] = date
       precipitation_dict["precipitation"] = prcp
       precipitation_data.append(precipitation_dict)


   return jsonify(precipitation_data)



@app.route("/api/v1.0/stations")
def stations():

   #Query the station data
   station_results = session.query(Station.name).all()

   session.close()

   # Create a list of station data
   station_data = list(np.ravel(station_results))
   
   return jsonify(station_data = station_data)



@app.route("/api/v1.0/tobs")
def tobs():

   #Query the temperature data
   start_date = dt.date(2016,8,23)
   temperature_results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= start_date).all()
   
   session.close()

   # Create list of temperature data
   temperature_data = list(np.ravel(temperature_results))

   return(jsonify(temperature_data = temperature_data))


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats (start = None, end = None):

   min_avg_max_function = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

   if not end:
      start = dt.datetime.strptime(start, "%m%d%Y")
      start_results = session.query(*min_avg_max_function).\
         filter(Measurement.date >= start).all()

      session.close()
      
      start_data = list(np.ravel(start_results))
      return(jsonify(start_data = start_data))
   
   start = dt.datetime.strptime(start, "%m%d%Y")
   end = dt.datetime.strptime(end,"%m%d%Y")

   start_end_results = session.query(*min_avg_max_function).\
      filter(Measurement.date >= start).\
      filter(Measurement.date <= end).all()
   
   session.close()

   start_end_data = list(np.ravel(start_end_results))
   return jsonify (start_end_data = start_end_data)

###

if __name__ == "__main__":
   app.run(debug=True)
