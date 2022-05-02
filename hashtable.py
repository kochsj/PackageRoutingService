class HashTable:
    """
    Hashtable data structure; holds package nodes in hashed-index buckets

    Has three public methods: add, get, and contains

    Parameters:
        {optional} [int] - length of hash table (number of buckets)
    """
    def __init__(self, length=1024):
        self._length_of_hash_table = length
        self._hash_table = [None] * self._length_of_hash_table


    def add(self, key, id, address, city, state, zip, deadline, weight, notes):
        """
        Takes key and package attributes as arguements

        Adds package to the HashTable at hash-index; Handles collisions

        Returns the added package (Package object)
        """
        # hash the key and assign index
        hashed_index = self._hash(key)
        #check for collision
        if not self._hash_table[hashed_index]:
            # no collision
            # create bucket at that index
            self._hash_table[hashed_index] = Bucket()

        #when there is and is not a collision we will be adding to the bucket
        pkg = Package(key, id, address, city, state, zip, deadline, weight)
        self._hash_table[hashed_index].add(pkg) # bucket method

        #add all of the restrictions
        if "Delayed" in notes:
            pkg.set_delayed_arrival(notes)
        if "Can only be on truck" in notes:
            if "1" in notes: pkg.set_truck_only(1)
            if "2" in notes: pkg.set_truck_only(2)
            if "3" in notes: pkg.set_truck_only(3)
        if "Must be delivered with" in notes:
            pkg.set_delivered_with(notes)
        if "Wrong address listed" in notes:
            pkg.set_wrong_address_listed(True)
        return pkg

    def get(self, key):
        """
        input: [string] - key

        retrieves a package from the hash table

        output: [Package object]
        """
        if self.contains(key):
            key_index = self._hash(key)
            return self._hash_table[key_index].return_value(key)
            
    def contains(self, key):
        """
        input: [string] - key

        checks that the hash table contains something at the key index

        output: [bool]
        """
        key_index = self._hash(key)
        if self._hash_table[key_index]:
            return self._hash_table[key_index].includes(key)
        return False

    def _hash(self, key):
        """
        Takes key as arguement
        Returns hash-index
        """
        #add ascii values of char together
        sum_chars = 0
        for char in key: 
            sum_chars += ord(str(char))
        #Square the sum
        square_sum = sum_chars**2
        #Floor devide by the first ascii value in key
        divide_square = square_sum // ord(key[0])
        #Mod length of hash table and return
        return (divide_square % self._length_of_hash_table)


class Bucket:
    """
    Linked-List data structure used at a filled index in HashTable to handle collisions

    Has three methods: add, includes, and return_value
    """
    def __init__(self):
        self.head = None

    def add(self, node):
        """
        Adds a node to the end of the linked list
        """
        _next_node = None
        if not self.head:
            self.head = node
            return

        if self.head.next:    
            _next_node = self.head.next
        else:
            self.head.next = node

        while _next_node:
            if not _next_node.next:
                _next_node.next = node
                break
            _next_node = _next_node.next
    
    def includes(self, key):
        """
        Determines if a given key is in the linked list
        """
        _next_node = self.head
        while _next_node:
            if _next_node.key == key:
                return True
            _next_node = _next_node.next
        return False

    def return_value(self, key):
        """
        input: [string] - key

        Returns a package from the hash table with the matching key

        output: [Package object]
        """      
        _current_node = self.head
        while _current_node:
            if _current_node.key == key:
                return _current_node
            _current_node = _current_node.next
        return None
                

class Package:
    """
    Node object that takes key / package attributes 
    
    Stored in the Hash Table 
    """
    def __init__(self, key, id, address, city, state, zip, deadline, weight):
        self.next = None
        self.key = key

        self._package_id = id
        self._address = address
        self._city = city
        self._state = state
        self._zip = zip
        self._deadline = deadline 
        self._weight = weight

        self.collision = False
        self._delayed_arrival = None
        self._truck_only = None
        self._delivered_with = None
        self._wrong_address_listed = False
        
        self._delivery_status = "at the hub"
        self._time_routed = None
        self._time_delivered = None

    def __repr__(self):
        return self._address

#### Package Methods (is_early, is_delayed, is_at_the_hub, has_collision)
    def is_early(self):
        """
        input: None

        checks if the package needs to be delivered early in the day

        output: [bool]
        """
        if "EOD" not in self._deadline:
            return True
        return False
    
    def is_delayed(self):
        """
        input: None

        checks if the package is arriving late to the hub

        output: [bool]
        """
        if self._delayed_arrival:
            return True
        return False
    
    def is_at_the_hub(self):
        """
        input: None

        checks if the package is still at the hub waiting to be routed

        output: [bool]
        """
        if self._delivery_status == "at the hub":
            return True
        return False
    
    def has_collision(self):
        """
        input: None

        checks if there are other packages that share the same address

        output: [bool]
        """
        return self.collision

    def print_status_and_info_at_given_time(self, time):
        """
        input: [int] - time; minutes from 00:00 hours

        prints package status and info at a given time to the command line interface

        output: None
        """
        _status = None
        if self._time_routed > time:
            _status = "at the hub"
        if self._time_delivered > time >= self._time_routed:
            _status = "en route"
        if time >= self._time_delivered:
            _status = "delivered"

        _d_time = None
        if _status == "delivered":
            _d_time = self._time_delivered
            hours = int(_d_time//60)
            minutes = int(_d_time%60)
            am_pm = " AM"
            if hours >= 12:
                am_pm = " PM"
            hours = str(hours)
            minutes = str(minutes)
            if len(minutes) == 1:
                minutes = "0" + minutes
            _d_time = hours + ":" + minutes + am_pm
        if _d_time:
            _status += f" {_d_time}"
        print(f"#{self._package_id} -- {self._address} {self._city}, {self._state} {self._zip} -- {self._weight}kg -- Deadline: {self._deadline} -- Status: {_status}")

#### Getters #################################################
    def get_package_id(self):
        """
        input: None

        output: [int] - package_id
        """
        return self._package_id
    
    def get_address(self):
        """
        input: None

        output: [string] - address
        """
        return self._address
    
    def get_city(self):
        """
        input: None

        output: [string] - city
        """
        return self._city
    
    def get_state(self):
        """
        input: None

        output: [string] - state
        """
        return self._state
    
    def get_zip(self):
        """
        input: None

        output: [int] - zip code
        """
        return self._zip
    
    def get_weight(self):
        """
        input: None

        output: [int] - weight
        """
        return self._weight
    
    def get_f_string(self):
        """
        input: None

        output: [string] - formatted string from excel sheet
        """
        return self.key
    
    def get_time_routed(self):
        """
        input: None

        output: [int] - time routed
        """
        return self._time_routed
    
    def get_time_delivered(self):
        """
        input: None

        output: [int] - time delivered
        """
        return self._time_delivered
    
    def get_delivered_with(self):
        """
        input: None

        output: [list[int]] - list of package ids
        """
        return self._delivered_with
    
    def get_wrong_address_listed(self):
        """
        input: None

        output: [bool]
        """
        return self._wrong_address_listed
    
    def get_delivery_status(self):
        """
        input: None

        output: [string] - delivery status
        """
        return self._delivery_status
    
    def get_truck_only(self):
        """
        input: None

        output: [int] - truck number
        """
        return self._truck_only
    
    def get_deadline(self):
        """
        input: None

        output: [float] - deadline; minutes from 00:00 hours
        """
        if not self._deadline or self._deadline == "EOD":
            return 1439.0 #11:59pm
        time_idx = self._deadline.index(':')
        if time_idx > 1:
            d_line = self._deadline[(time_idx-2):(time_idx+3)]
        else:
            d_line = self._deadline[(time_idx-1):(time_idx+3)]
        if len(d_line) == 5:
            hours = int(d_line[0:2])
            minutes = int(d_line[3:5])
        else:
            hours = int(d_line[:1])
            minutes = int(d_line[2:4])
        time = (hours*60) + minutes
        return time
    
    def get_delayed_arrival(self):
        """
        input: None

        output: [float] - delayed arrival; minutes from 00:00 hours
        """        
        time_idx = self._delayed_arrival.index(':')
        if time_idx > 1:
            d_line = self._delayed_arrival[(time_idx-2):(time_idx+3)]
        else:
            d_line = self._delayed_arrival[(time_idx-1):(time_idx+3)]
        if len(d_line) == 5:
            hours = int(d_line[0:2])
            minutes = int(d_line[3:5])
        else:
            hours = int(d_line[:1])
            minutes = int(d_line[2:4])
        time = (hours*60) + minutes
        return time

#### Setters #################################################
    
    def set_delivered_with(self, note):
        """
        input: [string] - note

        parses the note "must be delivered with x, y, z"; adds x,y,z as ints to delivered_with package attribute

        output: None
        """
        package_id_string = note[23:]
        substring = ''
        lst_of_package_id_ints = []

        for i, char in enumerate(package_id_string):
            if char == ' ':
                continue
            if char != ',' and char != ' ':
                substring += char
            if char == ',' or i == (len(package_id_string)-1):       
                lst_of_package_id_ints.append(int(substring))
                substring = ''
        self._delivered_with = lst_of_package_id_ints
    
    def update_delivered_with(self, pkg_id):
        """
        input: [int] - package_id

        adds a package id to the delivered_with package attribute

        output: None
        """
        if not self._delivered_with:
            self._delivered_with = [pkg_id]
        else:
            if pkg_id not in self._delivered_with:
                self._delivered_with.append(pkg_id)
    
    def set_delayed_arrival(self, note):
        """
        input: [string] - note

        parses the note "Delayed...xx:xx..."; finds the time xx:xx; sets delayed arrival attribute to the string xx:xx 

        output: None
        """
        arrival_time_idx = note.index(':')
        if arrival_time_idx > 1:
            arrival_time = note[(arrival_time_idx-2):(arrival_time_idx+3)]
        else:
            arrival_time = note[(arrival_time_idx-1):(arrival_time_idx+3)]
        if arrival_time[0] == ' ':
            arrival_time = arrival_time[1:]
        self._delayed_arrival = arrival_time   
    
    def set_collision(self, boolean):
        """
        input: [bool]

        sets collision package attribute True/False

        output: None
        """ 
        self.collision = boolean
    
    def set_time_routed(self, time): 
        """
        input: [int] - time; minutes from 00:00 hours

        sets time routed package attribute

        output: None
        """ 
        self._time_routed = time
    
    def set_time_delivered(self, time): 
        """
        input: [int] - time; minutes from 00:00 hours

        sets time delivered package attribute

        output: None
        """ 
        self._time_delivered = time
    
    def set_truck_only(self, truck_number): 
        """
        input: [int] - truck number

        sets truck only package attribute

        output: None
        """ 
        self._truck_only = truck_number
    
    def set_wrong_address_listed(self, b): 
        """
        input: [bool]

        sets wrong address listed package attribute True/False

        output: None
        """ 
        self._wrong_address_listed = b
    
    def set_delivery_status(self, status): 
        """
        input: [string] - status

        sets delivery status package attribute

        output: None
        """ 
        self._delivery_status = status
    
    def set_package_id(self, id): 
        """
        input: [int] - package id number

        sets package id attribute

        output: None
        """ 
        self._package_id = id
    
    def set_address(self, address): 
        """
        input: [string] - address

        sets address package attribute

        output: None
        """ 
        self._address = address
    
    def set_city(self, city): 
        """
        input: [string] - city

        sets city package attribute

        output: None
        """ 
        self._city = city
    
    def set_state(self, state): 
        """
        input: [string] - state

        sets state package attribute

        output: None
        """ 
        self._state = state
    
    def set_zip(self, z): 
        """
        input: [int] - zip code

        sets zip code  package attribute

        output: None
        """ 
        self._zip = z
    
    def set_weight(self, weight): 
        """
        input: [int] - weight

        sets package weight attribute

        output: None
        """ 
        self._weight = weight