# 1. import 
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from collections import defaultdict

connection_string = f"sqlite:///../Resources/hawaii.sqlite"

app = Flask(__name__)

db = create_engine(connection_string)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(db, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#static routes
precipitation_json_url = "api/v1.0/precipitation"
stations_json_url = "api/v1.0/stations"
tobs_last_year_active = "api/v1.0/tobs"

#dynamic routes
start_date_only_tobs = "api/v1.0/start"
start_end_dates_tobs = "api/v1.0/start/end"

@app.route('/')
def home():
    home_url = request.base_url
    output_html = "<h1>Hawaii Weather API</h1>"
    output_html += "<h3>Use the following routes to access API's</h3>"
    output_html += "<h3>Static Routes</h3>"
    output_html += "<ul>"
    output_html += f"<li><a href={home_url+precipitation_json_url}>/{precipitation_json_url}</a></li>"
    output_html += f"<li><a href={home_url+stations_json_url}>/{stations_json_url}</a></li>"
    output_html += f"<li><a href={home_url+tobs_last_year_active}>/{tobs_last_year_active}</a></li>"
    output_html += "</ul>"
    output_html += "<h3>Dynamic Routes</h3>"
    output_html += "<ul>"
    output_html += f"<li>/{start_date_only_tobs} with 'start' date in the format 2016-08-23 for August 23, 2016</li>"
    output_html += f"<li>/{start_end_dates_tobs} with 'start' and 'end' dates in the format 2016-08-23 for August 23, 2016</li>"
    output_html += "</ul>"
    return output_html

@app.route("/api/v1.0/precipitation")
def precipitation_json():
    #connect to the engine for this query
    session = Session(db)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
    date_to_precip = defaultdict(list)
    #list of precip values for each date in first dictionary
    for row in results:
        if(row[1] != None): date_to_precip[row[0]].append(row[1])
    #reduce the list of precipitation values to the max value for each date
    #to reflect "cleaned" data in notebook
    output_dict = {}
    for key in date_to_precip.keys():
        output_dict[key] = max(date_to_precip[key])
    #note that you can get all measured values, not just the max for each date
    #by changing the next line to jsonify(date_to_precip)
    return jsonify(output_dict)
    
@app.route("/api/v1.0/stations")
def stations_json():
    session = Session(db)
    results = session.query(Station.name, Station.longitude, Station.latitude, Station.elevation, Station.station).all()
    def map_Station_to_Dict(station_row):
        station_dict = {}
        station_dict["name"] = station_row[0]
        station_dict["longitude"] = station_row[1]
        station_dict["latitude"] = station_row[2]
        station_dict["elevation"] = station_row[3]
        station_dict["station"] = station_row[4]
        
        return station_dict
    output_list = [map_Station_to_Dict(row) for row in results]
    return jsonify(output_list)
        
@app.route("/api/v1.0/tobs")
def tobs_json():
    session = Session(db)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                                        filter(Measurement.date >= '2016-08-23').order_by(Measurement.date).all()
    date_to_tobs_most_active_last_year = {}
    for row in results:
        date_to_tobs_most_active_last_year[row[0]] = row[1]
        
    return jsonify(date_to_tobs_most_active_last_year)

#dynamic routes

@app.route("/api/v1.0/<start>")
def start_date_only_json(start):
    session = Session(db)
    
    min_temp_sql = session.query(func.min(Measurement.tobs)).\
                filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= start).order_by(Measurement.tobs).first()

    max_temp_sql = session.query(func.max(Measurement.tobs)).\
                filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= start).order_by(Measurement.tobs).first()

    avg_temp_sql = session.query(func.avg(Measurement.tobs)).\
                filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= start).order_by(Measurement.tobs).first()
    
    results = {"minimum": min_temp_sql, "average": avg_temp_sql, "maximum": max_temp_sql}
    
    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end_dates_json(start, end):
    session = Session(db)
    
    min_temp_sql = session.query(func.min(Measurement.tobs)).\
                filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.tobs).first()

    max_temp_sql = session.query(func.max(Measurement.tobs)).\
                filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.tobs).first()

    avg_temp_sql = session.query(func.avg(Measurement.tobs)).\
                filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.tobs).first()
    
    results = {"minimum": min_temp_sql, "average": avg_temp_sql, "maximum": max_temp_sql}
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)


