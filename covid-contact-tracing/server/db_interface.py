from datetime import datetime as dt
from entities import Event, Window, Status
from pymongo import MongoClient, errors
import json
from operator import attrgetter
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
baseDate = dt(2020,1,22,0,0,0,000)

def fetch_room_info(room_id):
    # print(room_id)
    room =  list(roomCollection.find({"id": room_id}, {'_id': 0}))
    return room[0] if room is not None else None

def fetch_last_user_record(user_id, room_id):
    #Fetch the last event with user_id and room_id with status as 'Entry'
    return {"rid": room_id, "uid": user_id, "status": 0, "timestamp": dt(2020, 4, 23, 19, 13, 34, 123)}


def add_room(room):
    roomCollection.insert([room])


def add_event(event):
    #Insert this record in events collection
    eventCollection.insert([event.__dict__])


def add_sanitized_event(event):
    #Insert this record in sanitized events collection
    sanitizedEventCollection.insert([event.__dict__])


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

def fetch_visit_events_of_user(user_id):
    ''' Returns list of event objects of all the rooms and their timestamps that are visited by the given user'''
    return [getEventObject(event) for event in sorted(list(eventCollection.find({"user_id":int(user_id)},{"_id":0})), key= lambda d : d['timestamp'])]
    

def fetch_entry_event(event):
    return getEventObject(list(eventCollection.find({"user_id":event.user_id, "room_id":event.room_id, "status":1 , "timestamp":{"$lt":event.timestamp}}, {"_id":0}))[-1])

def fetch_exit_event(event):
    return getEventObject(list(eventCollection.find({"user_id":event.user_id, "room_id":event.room_id, "status":0 , "timestamp":{"$gt":event.timestamp}}, {"_id":0}))[0])

def fetch_events_in_window(room_id, window):
    events = [getEventObject(event) for event in sorted(list(eventCollection.find({"room_id":room_id,"timestamp":{"$gte" : window.start, "$lte":window.end} },{"_id":0})), key= lambda d : d['timestamp'])]
    events.sort(key=attrgetter('user_id','timestamp'))
    closureList = []
    i=0
    while i < len(events):
        event = events[i]
        if(event.status==Status.EXIT):
            closureList.append(fetch_entry_event(event))
        elif(event.status==Status.ENTRY):
            if(i==len(events)-1 or (i<len(events)-1 and event.user_id!=events[i+1].user_id)) :
                closureList.append(fetch_exit_event(event))
            else:
                i+=2
                continue
        i+=1
    events+=closureList
    events = sorted(events, key = attrgetter('user_id','timestamp')) # Sort them with user_ids and timestamps, to make an entry exit pair
    return events         
        

def get_infected_window(room_id, visit_window):
    '''Returns window between agent's entry and end of the first sanitized time after the agent's exit'''
    
    #Infected window starts when the agent visits the room. Time before that doesn't matter
    start = visit_window.start
    
    # First cleaning window begin, after user has left
    safe_cleaning_time_begin = (list(sanitizedEventCollection.find({"room_id":room_id, "status":1 , "timestamp":{"$gte":visit_window.end}}, {"_id":0, "timestamp":1}))[0])['timestamp']
   
    #timestamp in sanitized collection for a time after the window end -- using safe time to begin cleaning 
    end =  (list(sanitizedEventCollection.find({"room_id":room_id, "status":0 , "timestamp":{"$gte":safe_cleaning_time_begin}}, {"_id":0, "timestamp":1}))[0])['timestamp']
    return Window(start, end) 


def getEventObject(event):
    return Event(event['user_id'],event['room_id'], event['status'], event['timestamp'])


if __name__ == "__main__":
    print(get_infected_window("B21970", Window(dt(2020, 1, 24, 9, 0, 0, 0), dt(2020, 1, 24, 19, 0, 0, 0))))