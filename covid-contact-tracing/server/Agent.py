from helper import get_infected_windows
from db_interface import fetch_rooms_visited, fetch_events_in_window
from contact_tracing import Overlap, RoomVisits, OverlappedUsers, Status
from operator import attrgetter

class Agent():
    def __init__(self, user_id):
        self.user_id = user_id
        self.room_visits = self.populate_room_visits()
        self.overlapped_users = self.populate_overlapped_users()
        
    def populate_room_visits(self):
        room_visits = RoomVisits()
        events = fetch_rooms_visited(self.user_id) #TODO: implementation needed
        for entry_event, exit_event in zip(events[0::2], events[1::2]):
            room_visits.get(entry_event['room_id']).add_agent_visit(entry_event['timestamp'], exit_event['timestamp'])
        return room_visits

    def populate_overlapped_users(self):
        overlapped_users = OverlappedUsers()
        room_visits = self.room_visits
        for room in room_visits:
                for infected_window in room.infected_windows :
                    events = fetch_events_in_window(room.room_id, infected_window) #TODO: implementation needed
                    self.populate_user_visit_windows(room, events, infected_window)
                #from the visit windows create , create overlap object -- iterate through room.user_visits
                for user_visit in room.user_visits:
                #Fetch the overlapped user with the user_id fetched from the events
                    overlapped_user = overlapped_users.get(user_visit.user_id)
                    for agent_visit in room.agent_visits:
                        if(user_visit.end >= agent_visit.start): # If he falls in potential infectant window
                            overlapped_user.add_overlap(Overlap(room.room_id, agent_visit, user_visit))
        return overlapped_users

    
    def populate_user_visit_windows(self, room, events, infected_window):
        events.sort(key = attrgetter('user_id', 'timestamp')) # Sort them with user_ids and timestamps, to make an entry exit pair
        for entry_event, exit_event in zip(events[0::2], events[1::2]):
            #filter agent events and all other events with both entry and exit before agent's first entry
            if(entry_event.user_id == self.user_id or exit_event.timestamp < infected_window.get_agent_visits()[0].start):
                continue
            self.room_visits.get(entry_event.room_id).add_user_visit(entry_event.user_id, entry_event.timestamp, exit_event.timestamp)