from algorithms import add_event_algo
from contact_tracing import Event
import datetime,json
from flask import Flask, request, url_for, redirect
app = Flask(__name__)

def getEventObj(event):
    return Event(event['user_id'], event['room_id'],
                     event['status'], event['timestamp'])


@app.route("/test")
def testMethod():
    return "Server running!"


@app.route("/addEvent", methods=["POST"])
def add_event():
    event = getEventObj(request.get_json())
    event.timestamp=datetime.datetime.now()
    print(event.status)
    # return str(add_event_algo(event))
    return json.dumps(add_event_algo(event), default=json_serial)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))