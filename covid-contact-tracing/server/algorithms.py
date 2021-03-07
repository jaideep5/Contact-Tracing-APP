from datetime import datetime as dt
import db_interface as db
from contact_tracing import Event


def add_event_algo(event):
    if event.status==1:
        return room_entry(event)
    else:
        return room_exit(event)

def room_entry(event):
    janitorFlag=False
    # print(room_id,user_id,timestamp,status)
    if isJanitor(event.user_id):
        # Mobile has to handle it's next operations based on this key
        janitorFlag=True
        room_clean(event)
    else:
        missing_events = handle_missing_events(event)
        if(missing_events != None):
            return missing_events
        db.add_event(event)
        update_room_capacity(
            event.room_id, event.status)
    room_info = db.fetch_room_info(event.room_id)
    if janitorFlag:
        room_info['clean_prompt'] = 1
    return room_info


def room_exit(event):
    if isJanitor(event.user_id):
        room_clean_exit(event)
    else:
        missing_events = handle_missing_events(event)
        if(missing_events != None):
            return missing_events
        db.add_event(event)
        update_room_capacity(
            event.room_id, event.status)
    return {"code": 200, "status": "Success"}


def update_room_capacity(room_id, status):
    room = db.fetch_room_info(room_id)
    current_capacity = room['current_strength'] or 0
    # current_capacity = 0 if current_capacity is None else current_capacity
    if status == status.EXIT:
        db.set_room_capacity(room_id, current_capacity-1)
    else:
        db.set_room_capacity(room_id, current_capacity+1)


def isJanitor(uid):
    return str(uid)[:3] == "BMP"


def handle_missing_events(event):
    return None
    old_rec = db.fetch_last_user_record(event.room_id, event.user_id)

    if event.status == 0:  # room exit
        if old_rec['status'] == 0:  # Missing current room entry
            return {"message": "Missing current room entry", "info": [{"room_id": event.room_id, "proposed_time": (dt.strptime(event.timestamp) + dt.timedelta(minutes=30))}]}

        # Missing current room entry and old room exit
        #FIXME: what if he enters old room at 7:00 and exits current room at 7:05?
        elif old_rec['status'] == 1 and old_rec['room_id'] != event.room_id:
            return {
                "message": "Missing current room entry and old room exit",
                "info": [
                    {"room_id": event.room_id, "proposed_time": dt.strptime(
                        event.timestamp) + dt.timedelta(minutes=30)},
                    {"room_id": old_rec['room_id'], "proposed_time": dt.strptime(
                        old_rec['timestamp']) + dt.timedelta(minutes=-30)}
                ]
            }
    else:  # room entry
        if old_rec['status'] == 1:  # Missing old room exit
            return {"message": "Missing old room exit", "info": [{"room_id": old_rec['room_id'], "proposed_time": dt.strptime(old_rec['timestamp']) + dt.timedelta(minutes=-30)}]}


def room_clean(event):
    db.add_sanitized_event(event)
    if event.status == 0:
        db.set_last_sanitized_ts(event.room_id, event.timestamp)
    else:
        db.set_last_sanitized_ts(event.room_id, ts=None)


def room_clean_exit(event):
    db.add_sanitized_event(event)
    db.set_last_sanitized_ts(event.room_id, ts=event.timestamp)


if __name__ == "__main__":
    event = Event("42225", "V29050", "0", "2020-01-22 00:04:09.085150")
    print(room_entry(event))
