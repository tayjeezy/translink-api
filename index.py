import requests
from google.transit import gtfs_realtime_pb2
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

GTFS_URL = "https://gtfsrt.api.translink.com.au/api/realtime/SEQ/TripUpdates"

@app.route("/stop/<stop_id>")
def get_stop_departures(stop_id):
    feed = gtfs_realtime_pb2.FeedMessage()
    r = requests.get(GTFS_URL)
    feed.ParseFromString(r.content)

    departures = []

    for entity in feed.entity:
        if entity.HasField("trip_update"):
            trip = entity.trip_update
            for stu in trip.stop_time_update:
                if stu.stop_id == stop_id:
                    if stu.arrival.time:
                        dt = datetime.fromtimestamp(stu.arrival.time)
                        departures.append({
                            "route": trip.trip.route_id,
                            "arrival": dt.isoformat()
                        })

    # sort by time
    departures.sort(key=lambda x: x["arrival"])

    return jsonify({
        "stop_id": stop_id,
        "departures": departures[:5]  # next 5 departures
    })

# For local testing
if __name__ == "__main__":
    app.run(debug=True)