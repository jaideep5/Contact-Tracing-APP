import random
from datetime import datetime, timedelta
from operator import attrgetter
from contact_tracing import Event, SanitizedEvent, Room, SanitizedStatus
import db_interface as db
import algorithms as algo
base = datetime(2020, 1, 22, 00, 00, 00)

room_names = ['Faner Hall', 'CS Main office', 'Linux Lab', 'Conference Room', 'Subway',
              'Grad School', 'Shryock Auditorium', 'REC center', 'Health Center', 'Campus Loop']


def gen_un(num=10):
    #  return [{"id" : random.randint(10001, 99999) , "role":"student"} for i in range(num)]
    return [random.randint(10001, 99999) for i in range(num)]


def gen_bmp_un(num=10):
    return ["BMP" + str(random.randint(10001, 99999)) for i in range(num)]


def gen_rid(num=10):
    return [chr(65 + random.randint(0, 25)) + str(random.randint(10001, 99999)) for i in range(num)]

# or a function


def gen_datetime(base, max_hour_limit=10):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    base += timedelta(hours=random.randint(0, max_hour_limit),
                      minutes=random.randint(1, 30), seconds=random.randint(0, 10), microseconds=random.randint(0, 100000))
    return base


def get_entry_exit_pairs(user_id, ridList, num=100):
    events = []
    start = base
    for i in range(num):
        room_id = ridList[random.randint(0, len(ridList)-1)]
        start = gen_datetime(start)
        if(start >= datetime.now()):
            break
        end = gen_datetime(start)
        events.append(Event(user_id, room_id, 1, start))
        events.append(Event(user_id, room_id, 0, end))
        start = end
    return events


def get_sanitized_events_for_the_day(unList, roomList, date, frequency=1):
    events = []
    random.shuffle(unList)
    random.shuffle(roomList)
    minLength = min(len(unList), len(roomList))
    for user_id, room_id in zip(unList[:minLength], roomList[:minLength]):
        baseTime = date
        for i in range(frequency):
            start = gen_datetime(baseTime, max_hour_limit=10)
            end = gen_datetime(start, max_hour_limit=1)
            events.append(SanitizedEvent(user_id, room_id, 1, start))
            events.append(SanitizedEvent(user_id, room_id, 0, end))
            baseTime = end
    return events


def addToFile(events, fname):
    f = open("covid-contact-tracing/server/mockdata/"+fname, "w")
    for event in events:
        f.write(str(event)+"\n")


def generate_room_entries(rooms):
    rooms.sort(key=attrgetter('id'))
    addToFile(rooms, f"room-by-id.txt")
    rooms.sort(key=attrgetter('name'))
    addToFile(rooms, f"room-by-name.txt")
    rooms.sort(key=attrgetter('max_capacity'))
    addToFile(rooms, f"room-by-capacity.txt")


def generate_mock_event_files(events, title):
    events.sort(key=attrgetter('user_id'))
    addToFile(events, f"{title}-user_id.txt")
    events.sort(key=attrgetter('room_id', 'timestamp'))
    addToFile(events, f"{title}-room_id.txt")
    events.sort(key=attrgetter('timestamp'))
    addToFile(events, f"{title}-timestamp.txt")


def main():
    global base
    unList = gen_un(100)
    bmpUserList = gen_bmp_un(10)
    ridList = gen_rid(10)
    random.shuffle(room_names)
    roomList = [Room(rid, room_names[i], random.randint(2, 100))
                for i, rid in enumerate(ridList)]
    all_events, all_sanitized_events = [], []
    for un in unList:
        base = datetime(2020, 1, 22, 00, 00, 00)
        all_events += (get_entry_exit_pairs(un, ridList, 100))

    for dayCount in range((datetime.now() - base).days):
        date = datetime(2020, 1, 22, 00, 00, 00) + timedelta(days=dayCount)
        all_sanitized_events += get_sanitized_events_for_the_day(
            bmpUserList, ridList,  date, frequency=2)

    generate_room_entries(roomList)
    #generate_mock_event_files(all_events, 'events')
    #generate_mock_event_files(all_sanitized_events, 'sanitized-events')

    #TODO: Add operations at 'one level up' -- handling things like, update_strength, update_last_sanitized_time, get_clean_window etc.
    # The latter two are needed for us to see how the algo works
    for room in roomList:
        db.add_room(room.__dict__)

    for event in sorted(all_events+all_sanitized_events, key=attrgetter('timestamp')):
        algo.add_event_algo(event)


    return all_events, all_sanitized_events


if __name__ == "__main__":
    main()
