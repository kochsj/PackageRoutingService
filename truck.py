class Truck:
    """
    Stack data structure with Truck attributes

    Three public stack methods: push, pop, and peek
    """
    def __init__(self, truck_number, departure_time=480):
        self._top = None

        self._num_packages = 0
        self._truck_number = truck_number
        self._daily_total_miles = 0
        self._departure_time = departure_time
        self._force_route = False
        self._daily_mileage_timeline = [(0, self._departure_time)]
        self._package_distance_at_time = []
        self._truck_rosters = []
    
    def __repr__(self):
        return (f"Truck#{self._truck_number}")

### Stack Methods (push, pop, peek)
    def push(self, package):
        """
        input: [Package object]

        push adds a package to the top of the truck's stack. sets delivery status to 'en route'

        output: None
        """
        top_pkg = self._top

        if top_pkg:
            package.next = top_pkg

        self._top = package
        self._num_packages += 1
        package.set_delivery_status('en route')

    def pop(self):
        """
        input: None

        pop removes the package at the top of the stack and returns

        output: [Package object]
        """
        top_pkg = self._top

        if top_pkg:
            next_top = top_pkg.next 
            top_pkg.next = None
            self._top = next_top
            self._num_packages -= 1
            top_pkg.set_delivery_status('at the hub')
            
        return top_pkg

    def peek(self):
        """
        input: None

        returns the package at the top of the stack

        output: [Package object]
        """
        return self._top

### Truck Methods (add_mileage, remove_mileage, clear_packages, is_empty, is_full, is_force_route, print_roster, print_miles_at_time, print_cumulative_mileage)
    def add_mileage(self, miles, time, is_pkg=True):
        """
        input: 
            [float] - miles, 
            [float] - time, 
            {optional}[bool] - is_pkg

        add_mileage adds mileage to the truck in three ways
        1. adds miles to the daily total for the truck
        2. adds a tuple (miles, time) to the daily timeline; provides reference to where the truck is at a given time
        3. adds a tuple (miles, time) to package removal timeline (for remove_mileage method)

        output: None
        """
        miles = round(miles,1)
        time = round(time,1)
        self._daily_total_miles += miles

        if is_pkg:
            self._package_distance_at_time.append((miles, time))

        if self._daily_mileage_timeline:
            prev = self._daily_mileage_timeline.pop()
            _cumulative_total = (prev[0] + miles)
            self._daily_mileage_timeline.append(prev)
            self._daily_mileage_timeline.append((_cumulative_total, time))

        else:
            self._daily_mileage_timeline.append((miles, time))

    def remove_mileage(self, time_to_remove):
        """
        input: [float] - time_to_remove

        remove_mileage removes the entry at time_to_remove from the package distance timeline

        output: [float] - miles
        """
        for i, cumulative_tuple in enumerate(self._daily_mileage_timeline):
            _time = cumulative_tuple[1]
            if _time == time_to_remove:
                del self._daily_mileage_timeline[i]
                break

        for i, time_tuple in enumerate(self._package_distance_at_time):
            _miles = time_tuple[0]
            _time = time_tuple[1]

            if _time == time_to_remove:
                self._daily_total_miles -= _miles
                del self._package_distance_at_time[i]
                return _miles

    def clear_packages(self, time=None):
        """
        input: [float] - time; minutes from 00:00 hours

        evacuates the stack, sets package status as delivered, saves the completed roster 

        output: None
        """
        time_str = self.time_to_string(time)

        if self._top:
            header = f"\nPackage Roster -- Route #{(len(self._truck_rosters)+1)} --  Returned to hub: {time_str}"
            route_roster = [header]

            while self._top:
                pkg = self.pop()
                pkg.set_delivery_status("delivered")
                roster_item = f"\t#{pkg.get_package_id()} -- {pkg} -- Deadline: {self.time_to_string(pkg.get_deadline())} -- Delivered at: {self.time_to_string(pkg.get_time_delivered())}"
                route_roster.append(roster_item)
            self.set_force_route(False)
            self._truck_rosters.append(route_roster)

    def is_empty(self):
        """
        input: None

        returns boolean if stack is empty

        output: [bool]
        """
        if self._num_packages == 0:
            return True
        return False

    def is_full(self):
        """
        input: None

        returns boolean if stack is full

        output: [bool]
        """
        if self._num_packages == 16:
            return True
        return False

    def is_force_route(self):
        """
        input: None

        returns boolean if truck is forced to route

        output: [bool]
        """
        return self._force_route

### Setters and Getters (get_daily_total_miles, get_departure_time, get_truck_number, get_mileage_at_time, set_departure_time, set_force_route)  
    def get_daily_total_miles(self):
        """
        input: None

        returns the total miles traveled by the truck for the day

        output: [float] - miles
        """
        return self._daily_total_miles

    def get_departure_time(self):
        """
        input: None

        returns the time the truck is scheduled to depart on it's current route

        output: [float] - departure time
        """
        return self._departure_time

    def get_truck_number(self):
        """
        input: None

        returns the truck's number

        output: [int] - truck number
        """
        return self._truck_number

    def get_mileage_at_time(self, time):
        """
        input: [int] - time; minutes from 00:00 hours

        returns the miles traveled for the day by the truck at the given time

        output: [float] - cumulative_distance_traveled
        """
        for i in range(len(self._daily_mileage_timeline)):
            idx = (len(self._daily_mileage_timeline) - 1) - i

            tuple = self._daily_mileage_timeline[idx] # (distance, time)
            t_time = tuple[1]

            if t_time < time and idx == (len(self._daily_mileage_timeline) - 1): # time is outside of the timeline
                return tuple[0]

            if t_time == time:
                return tuple[0]
            
            if t_time < time:
                time_diff = time - t_time
                dist = (time_diff * 18)/60
                cumulative_distance = tuple[0] + dist
                return cumulative_distance

    def get_packages_delivered_at_miles(self, miles):
        """
        input: [float] - cumulative miles traveled 

        returns the number of packages that have been delivered, given mileage on from the truck

        output: [int] - number of packages
        """
        counter = 0
        accumulation = 0
        for _pkg_tuple in self._package_distance_at_time: # (miles, time)
            accumulation += _pkg_tuple[0]
            if accumulation > miles:
                return counter
            counter += 1
        return counter

    def set_departure_time(self, d_time):
        """
        input: [int] - time; minutes from 00:00 hours

        sets the truck's departure time for it's current route

        output: None
        """
        self._departure_time = d_time

    def set_force_route(self, b):
        """
        input: [bool]

        sets the truck's force route property

        output: None
        """
        self._force_route = b

#### Print Methods (print_roster, time_to_string)
    def print_roster(self):
        for roster in self._truck_rosters:
            for item in roster:
                print(item)

    def time_to_string(self, time):
        if time == 1439:
            return "EOD"
        am_pm = " AM"
        hours = int(time//60)
        minutes = int(time%60)
        if hours >= 12:
            am_pm = " PM"
        hours = str(hours)
        minutes = str(minutes)
        if len(minutes) == 1:
            minutes = "0" + minutes
        time_str = hours + ":" + minutes + am_pm

        return time_str

    # def print_roster(self):
    #     """
    #     input: None

    #     prints the current route's package roster
    #     (package_id) -- (address) -- (time_delivered)

    #     output: None
    #     """
    #     top = self._top
    #     if top:
    #         print(f"#{top.get_package_id()} -- {top} -- Delivered at: {top.get_time_delivered()}") 
    #         # print(f"#{top.get_package_id()} -- {top} -- Delivered at: {top.get_time_delivered()} -- Early={top.is_early()} -- Miles: {self.get_mileage_at_time(top.get_time_delivered())}") 
    #         next = top.next
    #         while next:
    #             print(f"#{next.get_package_id()} -- {next}  -- Delivered at: {next.get_time_delivered()}") 
    #             # print(f"#{next.get_package_id()} -- {next}  -- Delivered at: {next.get_time_delivered()} -- Early={next.is_early()} -- Miles: {self.get_mileage_at_time(next.get_time_delivered())}") 
    #             next = next.next
    #     else: 
    #         print(f"{self} -- Empty -- No Packages on Route --  Return to hub at: {self._departure_time}")

            





