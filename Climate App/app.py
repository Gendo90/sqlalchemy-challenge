PGUSER="thistle_data"
PGPASS="Water.Lemon.Town"
PGDB="thistle"
PGPORT=5432
PGHOST="thistle-sample.crysldnompz3.us-west-2.rds.amazonaws.com"

# 1. import 
from flask import Flask, jsonify
from sqlalchemy import create_engine 

connection_string = f"postgres://{PGUSER}:{PGPASS}@{PGHOST}:{PGPORT}/{PGDB}"

app = Flask(__name__)

db = create_engine(connection_string)



@app.route('/')
def home():
    print(connection_string)
    return connection_string

@app.route("/api/data")
def get_data():
    results = db.execute('SELECT * FROM thistle_web.subscriptions_subscription')
    data_list = []
    for row in results:
        data_list.append({"id": row[0], "type": row[1] })
    return jsonify(data_list)
    


if __name__ == "__main__":
    app.run(debug=True)


