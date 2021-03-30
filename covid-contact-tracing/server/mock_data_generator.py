import random
from datetime import datetime, timedelta
from operator import attrgetter
from db_interface import add_room
from entities import Event, SanitizedEvent, Room, SanitizedStatus
import db_interface as db
import algorithms as algo
base = datetime(2020, 1, 22, 00, 00, 00)

room_names = ['Faner Hall', 'CS Main office', 'Linux Lab', 'Conference Room', 'Subway',
              'Grad School', 'Shryock Auditorium', 'REC center', 'Health Center', 'Campus Loop']


def gen_un(num=10):
    retVal = [70983, 67375, 38274, 15948, 39332, 46551, 89452, 65581, 91513, 56695, 93495, 14489, 33796, 22258, 35436, 28273, 15909, 49829, 91888, 41355, 12265, 25575, 13295, 94272, 75041, 79724, 94331, 49094, 97765, 76097, 27260, 79237, 56386, 41642, 76750, 19871, 80257, 18477, 84637, 46571, 44554, 84530, 48237, 71753, 77888, 33971, 60273, 54860, 29805, 20182, 50195, 69364, 69740, 66008, 36869, 90767, 76004, 17735, 70777, 92915, 87067, 63783, 49224, 86903, 81915, 56155, 35367, 50982, 90378, 96810, 49721, 29100, 34701, 53327, 35004, 51669, 85598, 38272, 80275, 59151, 50044, 27577, 69158, 33447, 63480, 44912, 57918, 46857, 77435, 76053, 15148, 16125, 54986, 31127, 38305, 65443, 29092, 75663, 98398, 48838]
    #[random.randint(10001, 99999) for i in range(num)]
    # print(retVal)
    return retVal


def gen_bmp_un(num=10):
    retVal = ['BMP32369', 'BMP85052', 'BMP26184', 'BMP95577', 'BMP75406', 'BMP50291', 'BMP87861', 'BMP16918', 'BMP72539', 'BMP80786']
    #["BMP" + str(random.randint(10001, 99999)) for i in range(num)]
    # print(retVal)
    return retVal


def gen_rid(num=10):
    retVal = ['J28929', 'P72143', 'S87978', 'L83225', 'B21970', 'S96687', 'L89485', 'D49972', 'G19247', 'S15838']
    #[chr(65 + random.randint(0, 25)) + str(random.randint(10001, 99999)) for i in range(num)]
    # print(retVal)
    return retVal

# or a function


def gen_datetime(base, max_hour_limit=10):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    base += timedelta(hours=random.randint(0, max_hour_limit),
                      minutes=random.randint(1, 30), seconds=random.randint(0, 10), microseconds=random.randint(0, 100000))
    return base


def get_entry_exit_pairs(user_id, ridList, num=100):
    events = []
    start = base
    for _ in range(num):
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
        for _ in range(frequency):
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
    generate_mock_event_files(all_events, 'events')
    generate_mock_event_files(all_sanitized_events, 'sanitized-events')

    for room in roomList:
        db.add_room(room.__dict__)

    for event in sorted(all_events+all_sanitized_events, key=attrgetter('timestamp')):
        algo.add_event_algo(event)


    return all_events, all_sanitized_events


if __name__ == "__main__":
    main()