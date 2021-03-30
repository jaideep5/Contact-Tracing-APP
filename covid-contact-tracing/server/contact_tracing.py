from entities import Event, Window, UserVisitWindow
from db_interface import get_infected_window
from datetime import timedelta
class InfectedWindows():
    """
        Similar to an iterator design pattern, this class has a dictionary of all the infected windows, 
        with key being the hashcode of the window
    """

    class InfectedWindow(Window):
        """ Given a visited window finds an infected window for that particular visit. Also contains all visited windows that fall within this"""
        def __init__(self, infected_window):
            super().__init__(infected_window.start, infected_window.end)
            self.agent_visit_windows = []
            self.user_visit_windows = []
        def add_agent_visit_window(self, visit_window):
        # Adds a visit window for this infected window
            self.agent_visit_windows.append(visit_window)

        def add_user_visit_window(self, visit_window):
        # Adds a visit window for this infected window
            self.user_visit_windows.append(visit_window)

        def get_agent_visits(self):
            return self.agent_visit_windows

    def __init__(self):
        self.infected_windows = {}

    def get(self, window):
        if window not in self.infected_windows:
            self.infected_windows[window] = self.InfectedWindow(window)
        return self.infected_windows[window]
#FIXME: This method is buggy --yielding inconsistent results. Try and fix it. Or kill it. 
    def merge_overlapping_windows(self):
        sorted_keys = sorted(self.infected_windows, key=lambda iw:iw.start)
        for iw1,iw2 in zip(sorted_keys[:-1],sorted_keys[1:]):
            if(iw2.start < iw1.end):
                new_iw_key = Window(min(iw1.start,iw2.start), max(iw1.end,iw2.end))
                new_iw = self.InfectedWindow(new_iw_key)
                new_iw.agent_visit_windows = list(set(self.infected_windows[iw1].agent_visit_windows).union(set(self.infected_windows[iw2].agent_visit_windows)))
                new_iw.user_visit_windows = list(set(self.infected_windows[iw1].user_visit_windows).union(set(self.infected_windows[iw2].user_visit_windows))) 
                del self.infected_windows[iw1],self.infected_windows[iw2]
                self.infected_windows[new_iw_key] = new_iw
    
    def __iter__(self):
        return iter(self.infected_windows.values())

class RoomVisits():
    class RoomVisit():
        def __init__(self, room_id):
            self.room_id = room_id
            self.infected_windows = InfectedWindows()

        def add_agent_visit(self, entry_timestamp, exit_timestamp):
            visit_window = Window(entry_timestamp, exit_timestamp)
            infected_window = get_infected_window(self.room_id, visit_window)
            self.infected_windows.get(infected_window).add_agent_visit_window(visit_window)

        def add_user_visit(self, user_id, entry_timestamp, exit_timestamp,infected_window):
            user_visit_window = UserVisitWindow(user_id, entry_timestamp, exit_timestamp)
            self.infected_windows.get(infected_window).add_user_visit_window(user_visit_window)

        def get_agent_visits(self):
            for window in self.infected_windows:
                for agent_visit in window.get_agent_visits():
                    yield agent_visit   

        def __str__(self):
            return str(self.room_id) + " - [" + ", ".join([str(agent_visit) for agent_visit in self.agent_visits]) +"]\n" \
                        + "Infected windows" + " - [" + ", ".join([str(infected_window) for infected_window in self.infected_windows]) +"]\n"  \
                         + "User Visits" + " - [" + ", ".join([str(user_visit) for user_visit in self.user_visits]) +"]\n" 

    def __init__(self):
        self.rooms = {}

    def get(self, room_id):
        if room_id not in self.rooms:
            self.rooms[room_id] = self.RoomVisit(room_id)
        return self.rooms[room_id]

    def __iter__(self) :
        return iter(self.rooms.values())

class OverlappedUsers():
    class OverlappedUser():
        def __init__(self, user_id):
            self.user_id = user_id
            self.overlaps = []
            self.total_overlap_duration = timedelta(seconds=0)
            self.overlap_frequency = 0
            self.direct_overlap_frequency = 0

        def add_overlap(self, overlap):
            if overlap not in self.overlaps:
                self.overlaps.append(overlap)
                self.total_overlap_duration += overlap.overlap_duration
                self.overlap_frequency+=1
                self.direct_overlap_frequency += 0 if overlap.overlap_duration == timedelta(seconds=0) else 1

        def __str__(self):
            retVal = "user_id: " +str(self.user_id) +"\nOverlap_frequency: "+ str(self.overlap_frequency) +"("+ str(self.direct_overlap_frequency) +" direct overlaps)\n total_overlap_duration: "+ str(self.total_overlap_duration) +"\n\tOverlaps:\n"
            for overlap in self.overlaps:
                retVal+=str(overlap)
            return retVal
            
            
    def __init__(self):
        self.users = {}

    def get(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = self.OverlappedUser(user_id)
        return self.users[user_id]

    def __iter__(self) :
        return iter(self.users.values())