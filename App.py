#Import required libraries:
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,desc

#importing Flask:
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Creating app
app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to my home page!<br/>"
        f"<br/>"
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> (date format must be YYYY-MM-DD, will return min max from all the stations)<br/>"
        f"/api/v1.0/<start>/<end> (date format must be YYYY-MM-DD, will return min max from all the stations)"
        
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    #Generate a queries to select the required data and send the statement directly to pandas dataframe
    prcpt = session.query(Measurement.date,Measurement.prcp).all()
    prcpt_dict = dict(prcpt)
    session.close()
    return jsonify(prcpt_dict)
    
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    station_mx=session.query(Measurement.station,func.count().label('Count')).group_by(Measurement.station).order_by(desc('Count')).first()    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago=dt.date(int(last_date[0][0:4]),int(last_date[0][5:7]),int(last_date[0][8:10])) - dt.timedelta(days=365)
    tobs_st = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= str(year_ago),Measurement.date <= last_date[0],Measurement.station == station_mx[0]).all()

    session.close()
    return jsonify(tobs_st)


@app.route("/api/v1.0/<start>/<end>")
def statis_1(start,end):
    session = Session(engine)
    #tobs_st1 = session.query(Measurement.tobs).filter(Measurement.date >= str(start)).order_by(desc(Measurement.tobs)).first()
    tobs_st1 = session.query(func.avg(Measurement.tobs).label("TAVG"),func.max(Measurement.tobs).label("TMAX"), func.min(Measurement.tobs).label("TMIN")).filter(Measurement.date>= start,Measurement.date <= end)
    
    res = tobs_st1.one()
    minimum = res.TMIN
    maximum = res.TMAX
    average = round(res.TAVG,2)

    session.close()
    return (f"Maximum temperature from all the stations is {maximum}<br/>"
            f"Minimum temperature from all the stations is {minimum}<br/>"
            f"Average temperature from all the stations is {average}<br/>")

@app.route("/api/v1.0/<start>")
def statis_2(start):
    session = Session(engine)
    #tobs_st1 = session.query(Measurement.tobs).filter(Measurement.date >= str(start)).order_by(desc(Measurement.tobs)).first()
    tobs_st1 = session.query(func.avg(Measurement.tobs).label("TAVG"),func.max(Measurement.tobs).label("TMAX"), func.min(Measurement.tobs).label("TMIN")).filter(Measurement.date>= start)
    
    res = tobs_st1.one()
    minimum = res.TMIN
    maximum = res.TMAX
    average = round(res.TAVG,2)

    session.close()
    return (f"Maximum temperature from all the stations is {maximum}<br/>"
            f"Minimum temperature from all the stations is {minimum}<br/>"
            f"Average temperature from all the stations is {average}<br/>")

if __name__ == "__main__":
    app.run(debug=True)