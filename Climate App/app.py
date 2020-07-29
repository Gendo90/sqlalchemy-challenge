# 1. import 
from flask import Flask, jsonify, request
from sqlalchemy import create_engine
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


precipitation_json_url = "api/v1.0/precipitation"

@app.route('/')
def home():
    home_url = request.base_url
    output_html = "<h1>Hawaii Weather API</h1>"
    output_html += "<h3>Use the following routes to access API's</h3>"
    output_html += "<ul>"
    output_html += f"<li><a href={home_url+precipitation_json_url}>/{precipitation_json_url}</a></li>"
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
    


if __name__ == "__main__":
    app.run(debug=True)


