from datetime import datetime as dt
from contact_tracing import Event
from pymongo import MongoClient, errors
import json
DB_LOCAL = {
    "uri": 'localhost',
    "port": 27017,
    "dbname": "contact-tracing",
    "un": "",
    "pwd": "",
    "rooms": "roomsCollection",
    "events": "eventsCollection",
    "sanitizedEvents": "sanitizedEventsCollection"
}
dbConf = DB_LOCAL

client = MongoClient(dbConf['uri'], dbConf['port'], username=dbConf['un'],
                     password=dbConf['pwd'], authsource=dbConf['dbname'])
db = client[dbConf["dbname"]]
eventCollection = db[dbConf['events']]
roomCollection = db[dbConf['rooms']]
sanitizedEventCollection = db[dbConf['sanitizedEvents']]


def fetch_room_info(room_id):
    return list(roomCollection.find({"id": room_id}, {'_id': 0}))[0]


def fetch_last_user_record(user_id, room_id):
    #Fetch the last event with user_id and room_id with status as 'Entry'
    return {"rid": room_id, "uid": user_id, "status": 0, "timestamp": dt(2020, 4, 23, 19, 13, 34, 123)}


def add_room(room):
    roomCollection.insert([room])


def add_event(event):
    #Insert this record in events collection
    eventCollection.insert([event.__dict__])
    pass


def add_sanitized_event(event):
    #Insert this record in sanitized events collection
    sanitizedEventCollection.insert([event.__dict__])
    pass


def set_room_capacity(room_id, capacity):
    roomCollection.update(
        {"id": room_id}, {"$set": {"current_strength": capacity}})


def set_last_sanitized_ts(room_id, ts):
    if ts == None:
        roomCollection.update(
            {"id": room_id}, {"$set": {"last_sanitized_time": "Cleaning in progress"}})
    else:
        roomCollection.update(
            {"id": room_id}, {"$set": {"last_sanitized_time": ts}})

def fetch_rooms_visited(user_id):
    return []  # rooms


def fetch_overlapped_users(user_id, room_id, timestamp):
    return []  # List of user objects


def fetch_events_in_window(room_id, window):
    return []


if __name__ == "__main__":
    print(fetch_room_info("Y85525"))
