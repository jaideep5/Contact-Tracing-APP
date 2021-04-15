from db_interface import fetch_visit_events_of_user, fetch_events_in_window, get_infected_window
from entities import Overlap, Status
from contact_tracing import RoomVisits, OverlappedUsers
from operator import attrgetter

class Agent():
    def __init__(self, user_id):
        self.user_id = user_id
        self.room_visits = self.populate_room_visits()
        # self.__handle_overlapping_infected_windows()  #FIXME: The lower level implementation of the algo is buggy
        self.overlapped_users = self.populate_overlapped_users()
        
    def populate_room_visits(self):
        room_visits = RoomVisits()
        events = fetch_visit_events_of_user(self.user_id) 
        for entry_event, exit_event in zip(events[0::2], events[1::2]):
            room_visits.get(entry_event.room_id).add_agent_visit(entry_event.timestamp, exit_event.timestamp)
        return room_visits

    def __handle_overlapping_infected_windows(self):
        for room in self.room_visits:
            room.infected_windows.merge_overlapping_windows()

    def populate_overlapped_users(self):  
        overlapped_users = OverlappedUsers()
        for room in self.room_visits:
                for infected_window in room.infected_windows :
                    events = fetch_events_in_window(room.room_id, infected_window) 
                    self.populate_user_visit_windows(room, events, infected_window)
                    for user_visit in infected_window.user_visit_windows:
                        overlapped_user = overlapped_users.get(user_visit.user_id)
                        for agent_visit in infected_window.agent_visit_windows:
                            if(user_visit.end >= agent_visit.start): # If he falls in potential infected window
                                overlapped_user.add_overlap(Overlap(room.room_id, agent_visit, user_visit, infected_window))
        return overlapped_users

    
    def populate_user_visit_windows(self, room, events, infected_window):
        for entry_event, exit_event in zip(events[0::2], events[1::2]):
            #filter out  agent events
            if(entry_event.user_id == self.user_id):
                continue
            self.room_visits.get(entry_event.room_id).add_user_visit(entry_event.user_id, entry_event.timestamp, exit_event.timestamp, infected_window)

if __name__ == "__main__":
    agent = Agent(36869)

    # #push output to overlap.txt in mockdata
    # for ou in agent.overlapped_users:
    #          print(ou)

    #push output to visits_and_windows.txt in mockdata
    for rv in agent.room_visits:
        print("Room - "+rv.room_id)
        print("Agent Visits")
        for av in rv.get_agent_visits():
            print(av)
        
        for iw in rv.infected_windows:
            print("\nInfected Window:-")
            print(iw)
            print("User Visits")
            for uv in iw.user_visit_windows:
                print(uv)