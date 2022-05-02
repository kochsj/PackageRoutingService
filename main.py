# --------------------------------------------------------------------
# |             DATA STRUCTURES AND ALGORITHMS II — C950             |
# |                   TASK 1: WGUPS ROUTING PROGRAM                  |
# |                           Stephen Koch                           |
# |                       Student ID: 001435707                      |
# |__________________________________________________________________|
import os
import data
import hashtable
import graph
import truck

if __name__ == "__main__":

########################################################################################
### Set up data structures(hashtable, graph, stacks) ####################################
########################################################################################

    # Instanciate the HashTable to store the Day's Packages. 
    daily_hash_table = hashtable.HashTable()
    
    # Instanciate the Graph that will be used to measure all distances. Fill graph with the Day's packages
    distance_graph = graph.Graph()
    
    # set up trucks
    # the hub has three trucks but only two drivers. So we will consider only two trucks for the algorithm
    truck1 = truck.Truck(truck_number=1)
    truck2 = truck.Truck(truck_number=2)

########################################################################################
### Helper Functions ###################################################################
########################################################################################
    def find_row_in_matrix(u_address):
        """
        input: [string] - address

        using the address, finds the corresponding row from the distance table

        output: [list[int]] - row from distance table
        """
        for i, d_address in enumerate(d_addresses):
            if u_address in d_address:
                row = distance_matrix[i]
                return row
    def find_u_address(f_string_address):
        """
        input: [string] - formatted string from package file

        searches the formatted string for an address from the unique addresses

        output: [string] - unique address
        """
        for u_address in unique_addresses:
            if u_address in f_string_address:
                return u_address
    def add_distance_edges(graph, list_of_keys):
        """
        input:
            [graph] - distance graph
             [list[string]] - list of keys,

        adds distance edges to the graph for every package between every other package from the package file

        output: None
        """
        for pkg_a_key in list_of_keys: # for every package (a)
            pkg_a = daily_hash_table.get(pkg_a_key)
            row_in_matrix = find_row_in_matrix(pkg_a.get_address())
            for pkg_b_key in list_of_keys: # for every other package (NOT-a)
                if pkg_b_key is not pkg_a_key:
                    u_address_b = find_u_address(pkg_b_key)
                    for i, d_address in enumerate(d_addresses):
                        if u_address_b in d_address:
                            dst = row_in_matrix[i]
                            pkg_b = daily_hash_table.get(pkg_b_key)
                            graph.add_edge(pkg_a, pkg_b, dst)
    def add_packages_to_hashtable_and_graph(list_of_packages, hashtable, graph):
        """
        input: 
            [list[list[package attributes]]] - 2D list of package attributes from Package file,
             [hashtable] - daily package hash table,
            [graph] - distance graph

        adds packages to hash table and to graph

        output: None
        """
        for list in list_of_packages:
            pkg = hashtable.add(list[0],list[1],list[2],list[3],list[4],list[5],list[6],list[7],list[8]) # adding (key(f_string), id, address, city, state, zip, deadline, weight, notes)
            graph.add_package(pkg)
    def calculate_delivery_time(miles):
        """
        input: [float] - miles

        calculates delivery time based on 18mph average

        output: [float] - minutes
        """
        mph = 18
        hours = miles/mph
        minutes = round((60*hours), 0)
        return minutes
    def find_distance_between_x_and_y(package_x, package_y):
        """
        input: 
            [Package object] - package_x,
             [Package object] - package_y

        finds the distance, in miles, between x and y

        output: [float] - miles
        """
        u_address = find_u_address(package_x.get_f_string())
        neighbor_list = distance_graph.get_adj_list(u_address)
        
        for edge in neighbor_list[1:]:
            if edge[0] == package_y:
                return edge[1]
    def package_can_be_added_to_truck(package, truck, delivery_time):
        """
        input: 
            [Package object] - package to be added to truck,
             [Truck object] - truck to be added to,
            [int] - delivery time; minutes from 00:00 hours

        determines if the given package can be added to the given truck and meet all the package's requirements for delivery

        output: [bool] - True/False
        """
        # verify that the package is valid to be added to the truck
        # set information on package restrictions
        early = package.is_early()
        collision = package.has_collision()
        delayed = package.is_delayed()
        truck_only = package.get_truck_only()
        wrong_address = package.get_wrong_address_listed()

        if not package.is_at_the_hub():
            return False
        if collision:
            adj_lst = distance_graph.get_adj_list(package.get_address())
            pkg_at_same_address = adj_lst[0]
            t_only = None

            for pkg in pkg_at_same_address:
                if pkg is not package: # ignore itself
                    current_t_only = pkg.get_truck_only()
                    if not t_only and current_t_only:
                        t_only = current_t_only
                    if t_only and current_t_only:
                        # multiple packages going to the same address are requiring to be sent on specific trucks
                        # check if they are not the same truck
                        if t_only is not current_t_only:
                            # then ignore collison and add as you please to the truck
                            t_only = None
                            break
            if t_only:
                if t_only is not truck.get_truck_number():
                    return False

        if early:
            deadline = package.get_deadline()
            if delivery_time > deadline:
                # package will not arrive by the deadline
                return False

        if delayed:
            arrival_time = package.get_delayed_arrival()
            departure_time = truck.get_departure_time()
            if arrival_time > departure_time:
                # package is arriving after the truck is slotted to leave the hub
                return False

        if truck_only:
            if truck_only != truck.get_truck_number():
                # package needs to be on a different truck
                return False

        if wrong_address:
            return False
            
        return True
    def update_delivered_with(hashtable, keys):
        """
        input: 
            [hashtable] - daily package hash table,
             [list[string]] - list of package keys

        Updates packages that have other packages that they need to be delivered with. 
        
        If (A) needs to be delivered with (B), then update B so that (B) needs to be delivered with (A)

        output: None
        """
        for key in keys:
            pkg = hashtable.get(key) #14
            lst = pkg.get_delivered_with()
            if lst: # [15,19]
                for _id in lst:
                    for k in keys:
                        p = hashtable.get(k)
                        if p.get_package_id() == _id:
                            p.update_delivered_with(pkg.get_package_id())
    def fix_incorrect_address(pkg_number, arrival_time_string, address, city, state, zip):
        """
        input: 
            [int] - package id number,
             [string] - arrival time; xx:xx format,
            [string] - address,
             [string] - city,
            [string] - state,
             [int] - zip code

        corrects an incorrect address for a package in the hashtable

        output: None
        """
        _pkg = None
        for f in package_f_string_list:
            p = daily_hash_table.get(f)
            if p.get_package_id() == pkg_number:
                _pkg = p
                break
        if _pkg.get_wrong_address_listed():
            _pkg.set_wrong_address_listed(False)
            _pkg.set_delayed_arrival(arrival_time_string)
            _pkg.set_address(address)
            _pkg.set_city(city)
            _pkg.set_state(state)
            _pkg.set_zip(zip)
    def ensure_timely_delivery(list_of_truck_tuples):
        """
        input: [list[(Truck object, int)]] - list of tuples (Truck, time_returning_to_hub)

        ensures that IF there are packages with deadlines still at the hub after the trucks leave, that they will be delivered on time when the trucks return

        adjusts the roster of packages on the truck if needed in order to ensure all packages arrive by their deadline via check_truck_for_package_replacement()

        output: None
        """
        # list_of_truck_tuples:[(Truck1, time_returning_to_hub), (Truck2, time_returning_to_hub)]
        truck1 = list_of_truck_tuples[0][0]
        truck1_departure_time = truck1.get_departure_time()
        truck1_arrival_time = list_of_truck_tuples[0][1]

        truck2 = list_of_truck_tuples[1][0]
        truck2_departure_time = truck2.get_departure_time()
        truck2_arrival_time = list_of_truck_tuples[1][1]
        earlies = []

        hub = daily_hash_table.get(package_f_string_list[0])

        for f_string in package_f_string_list:
            _pkg = daily_hash_table.get(f_string)
            if _pkg.is_at_the_hub() and _pkg.is_early():
                earlies.append(_pkg)
        for early in earlies:
            if early.is_delayed() and truck2_arrival_time == 480:
                truck2.set_departure_time(early.get_arrival_time())
                break

        for early in earlies:
            deadline = early.get_deadline()
            distance = find_distance_between_x_and_y(hub, early)
            time_from_hub = calculate_delivery_time(distance)
            truck1_arrival_time += time_from_hub

            if truck1_arrival_time > deadline:
                truck1_arrival_time -= time_from_hub
                truck2_arrival_time += time_from_hub
                if truck2_arrival_time > deadline:
                    truck2_arrival_time -= time_from_hub
                    # now we need to start traversing the stacks and remove a package to replace with the early
                    if check_truck_for_package_replacement(truck1, truck1_departure_time, time_from_hub, deadline, early):
                        # Returning True means that the early was successfully added to truck 1
                        continue
                    if check_truck_for_package_replacement(truck2, truck2_departure_time, time_from_hub, deadline, early):
                        # Returning true means that the package was added to truck2
                        continue
                else:
                    # the early could be on truck2 after it returns to the hub
                    pass

            else:
                # the early could be on truck1 after it returns to the hub from its route
                pass
    def check_truck_for_package_replacement(truck, truck_departure_time, time_from_hub, deadline, package_to_be_added):
        """
        input: 
            [Truck object] - truck to check
             [int] - truck departure time; minutes from 00:00 hours
            [int] - time to deliver from hub; minutes
             [int] - deadline; minutes from 00:00 hours
            [Package object] - package to be added

        adjusts the roster of packages on the truck if needed in order to ensure all packages arrive by their deadline

        searches the Truck stack for a position that the package to be added can be pushed, allowing it to be delivered on time

        reroutes the truck if a position on the stack is found via find_nearest_neighbor_path()

        output: [bool] - True/False
        """
        # traversing stack and removing package to replace with early:
        # get truck departure time
        # add the time it would take for the package to be delivered from the hub
        truck_departure_time += time_from_hub
        if truck_departure_time > deadline:
            # it is impossible to add to the truck even if it is the first package.
            # no need to search the truck's stack
            truck_departure_time -= time_from_hub
            return False
        else:
        #     it could fit on there some where
        #     pop off of truck stack until you can add
        #     ignore delivered_with, collisions, and other earlies
            other_early = []
            removed = []
            delivery_time = None

            if truck.is_full():
                _top = truck.pop()
                _time = _top.get_time_delivered()
                _dist = truck.remove_mileage(_time)
                _top.set_time_delivered(None)
                _top.set_time_routed(None)
                removed.append((_top, _dist, _time))

            for i in range(16):
                _pkg_popped_from_stack = truck.pop()
                _time = _pkg_popped_from_stack.get_time_delivered()
                _dist = truck.remove_mileage(_time)

                if _pkg_popped_from_stack:
                    removed.append((_pkg_popped_from_stack, _dist, _time))
                    has_collision = _pkg_popped_from_stack.has_collision()
                    has_delivered_with = _pkg_popped_from_stack.get_delivered_with()
                    is_early =_pkg_popped_from_stack.is_early()
                
                    if has_collision:
                        continue
                    if has_delivered_with:
                        continue
                    if is_early:
                        other_early.append(_pkg_popped_from_stack)
                        continue

                    distance = find_distance_between_x_and_y(_pkg_popped_from_stack, package_to_be_added)
                    time_from_pkg_popped_from_stack = calculate_delivery_time(distance)
                    delivery_time = (_pkg_popped_from_stack.get_time_delivered() + time_from_pkg_popped_from_stack)
                    
                else:
                    # reached the end of the stack
                    # going to add the package, then other earlies
                    delivery_time = truck_departure_time + time_from_hub

                if delivery_time > deadline:
                    # package cannot be added yet. continue popping off the truck stack
                    _pkg_popped_from_stack.set_time_delivered(None)
                    _pkg_popped_from_stack.set_time_routed(None)
                    continue
                else:
                    # package can be added at this point.
                    if _pkg_popped_from_stack:
                        truck.push(_pkg_popped_from_stack)
                        _pkg_popped_from_stack.set_time_delivered(_time)
                        _pkg_popped_from_stack.set_time_routed(truck.get_departure_time())
                        truck.add_mileage(_dist, _time)

                    truck.push(package_to_be_added)
                    package_to_be_added.set_time_delivered(delivery_time)
                    package_to_be_added.set_time_routed(truck.get_departure_time())

                    truck.add_mileage(distance, delivery_time)
                    keep_looking = False

                    # find out if the package_to_be_added has any collisions at it's address; we want to try to deliver them at the same time
                    if package_to_be_added.has_collision():
                        neighbors = distance_graph.get_adj_list(package_to_be_added.get_address())
                        pkg_at_the_same_address = neighbors[0]
                        for _pkg in pkg_at_the_same_address:
                            if _pkg is not package_to_be_added:
                                if package_can_be_added_to_truck(_pkg, truck, delivery_time):
                                    truck.push(_pkg)
                                    _pkg.set_time_delivered(delivery_time)
                                    _pkg.set_time_routed(truck.get_departure_time())

                                    truck.add_mileage(0, delivery_time)               

                    # add back the other earlies that were skipped originally
                    if other_early:
                        distance = None
                        for other in other_early:
                            if not distance:
                                distance = find_distance_between_x_and_y(package_to_be_added, other)
                                time_from_other = calculate_delivery_time(distance)
                                other_del_time = (delivery_time + time_from_other)
                            else:
                                _measure_from = truck.peek()
                                distance = find_distance_between_x_and_y(_measure_from, other)
                                time_from_other = calculate_delivery_time(distance)
                                other_del_time = (_measure_from.get_time_delivered() + time_from_other)

                            if other_del_time > other.get_deadline():
                                # need to keep looking. other early will now be late
                                if _pkg_popped_from_stack:
                                    truck.pop() #_pkg_popped_from_stack
                                    _pkg_popped_from_stack.set_time_delivered(None)
                                    _pkg_popped_from_stack.set_time_routed(None)
                                    truck.remove_mileage(_time)
                                truck.pop() # package
                                package_to_be_added.set_time_delivered(None)
                                package_to_be_added.set_time_routed(None)
                                truck.remove_mileage(delivery_time)                            

                                keep_looking = True

                                if not _pkg_popped_from_stack:
                                    return 
                                break
                            else:
                                # all earlies from other early can be added to the truck
                                truck.push(other)
                                other.set_time_routed(truck.get_departure_time())
                                other.set_time_delivered(other_del_time)

                                truck.add_mileage(distance, other_del_time)
                if keep_looking:
                    continue
                else:                 
                    # re-route the rest of the truck
                    find_nearest_neighbor_path(package_to_be_added, truck, delivery_time)
                return True

        return False            
    def convert_to_twenty_four_hour(time):
        """
        input: [int] - time; minutes from 00:00 hours

        converts integer time to 24-hour format

        output: [string] - 24-hour time
        """
        hours = time//60
        minutes = (time - (hours*60))
        time = f"{hours}:{minutes}"
        return time

########################################################################################
### Nearest Neighbor Algorithm #########################################################
########################################################################################
    def find_nearest_neighbor_path(package, truck, current_time):
        """
        input:
            [Package object] - starting package to find the nearest neighbor of
             [Truck object] - truck packages are being routed on
            [int] - current time; minutes from 00:00 hours

        Recursive function that takes a starting package and continualy finds the nearest VALID neighbor - meets all package requirements.

        Groups packages at the same address (hashtable collisions) and packages that it must be delivered with

        Continues routing until one of three base cases:
        1) truck is full
        2) No more packages available to route
        3) truck is set to force_route

        output: [tuple] - (truck, time_returning_to_hub)
        """     
        # list of nearest package(s) that are to be added to truck 
        pkg_to_add_to_truck = []
        # 1. Get the unique address of the starting package - to get the correct adj_list from the distance graph
        f_string = package.get_f_string()
        u_address = find_u_address(f_string)
        adj_list = distance_graph.get_adj_list(u_address) # [[Package Object(s)], {edge:(Pkg, distance)}, {edge:(Pkg, distance)},...]
        neighbor_edges = adj_list[1:]

        # 2. find the first valid starting point in neighbor_edges for comparison between next nearest neighbor in the remainder of the list
        closest_package = None
        current_distance = 0

        for tuple in neighbor_edges:
            _pkg = tuple[0]
            _delivery_time = calculate_delivery_time(tuple[1])
            _delivery_time += current_time
            # check if the package is still at the hub, and can be added to the truck -- otherwise it has been routed or has other restrictions; ignore it and continue
            if package_can_be_added_to_truck(_pkg, truck, _delivery_time):
                # END #2 - package is valid to be on the truck. Set it as the starting package to begin comparison in pt. 3
                closest_package = _pkg
                current_distance = tuple[1]
                break

        # BASE CASE -- end of recursion -- there are no valid packages to even begin to compare. return the truck to hub
        if closest_package == None:
            distance_to_hub = 0
            if not package.get_package_id() == 0:
                # then package left the hub.
                # get the distance to return back to the hub for more packages
                for tuple in neighbor_edges:
                    package_id = tuple[0].get_package_id()
                    if package_id == 0:
                    
                        distance_to_hub = tuple[1]
                        break

            # add the time it takes to return to the hub to the "current time"
            time_to_return_to_hub = calculate_delivery_time(distance_to_hub)
            time_arriving_at_hub = current_time + time_to_return_to_hub

            # truck.add_mileage(distance_to_hub, time_arriving_at_hub, no_pkg=True)
            return (truck, time_arriving_at_hub)
        
        # 3. Compare all neighbors to find actual closest neighbor that still needs to be delivered and is not 'restricted'
        for tuple in neighbor_edges:
            _pkg = tuple[0]
            _dst = tuple[1]

            # check that the distance is less than the "current" shortest distance
            if _dst < current_distance:
                # _miles = find_distance_between_x_and_y(package, _pkg)
                _delivery_time = calculate_delivery_time(_dst)
                _delivery_time += current_time
                # make sure that the closer package still needs to be delivered and can be delivered
                if package_can_be_added_to_truck(_pkg, truck, _delivery_time):
                    # package is therefore valid to be on the truck and is closer than the previous closest_package. Update closest_package and distance for next comparison
                    closest_package = _pkg
                    current_distance = _dst

        # END 3 - closest_package has been assigned to the package that is closest and is valid to be added to the truck for delivery. current_distance is assigned the distance to closest_package
        pkg_to_add_to_truck.append((closest_package, current_distance))

        # 4. Check for hashtable collisions at closest_package - the goal is to add all packages to the truck that are going to the exact same address for efficency
        if closest_package.has_collision():
            edges_from_distance_graph = distance_graph.get_adj_list(closest_package.get_address())
            list_of_package_at_same_address = edges_from_distance_graph[0]

            for _pkg in list_of_package_at_same_address:
                if _pkg is not closest_package:
                    _miles = find_distance_between_x_and_y(package, _pkg)
                    _delivery_time = calculate_delivery_time(_miles)
                    _delivery_time += current_time
                    if package_can_be_added_to_truck(_pkg, truck, _delivery_time):
                        pkg_to_add_to_truck.append((_pkg, 0)) # no distance to same address -- {tuple:(Package Obj, distance)}
            

        # 5. Check for packages "delivered with" the closest_package -- these need to be on the same truck
        # get_delivered_with() returns a list of package_id numbers: [13,15,18] OR an empty list: []
        delivered_with = closest_package.get_delivered_with()
        if delivered_with:
            # match the id_numbers from delivered_with with Packages from the neighbor_edges
            for _id in delivered_with:
                for tuple in neighbor_edges: # (Package Object, distance)
                    if tuple[0].get_package_id() == _id:
                        _delivery_time = calculate_delivery_time(tuple[1])
                        _delivery_time += current_time
                        if package_can_be_added_to_truck(tuple[0], truck, _delivery_time):
                            # get the packages that must be delivered with that package as well. append them to delivered_with list. they will be checked for their delivered with as well and so on...
                            also_must_be_delivered_with = tuple[0].get_delivered_with()
                            if also_must_be_delivered_with:
                                for pid in also_must_be_delivered_with:
                                    if pid not in delivered_with:
                                        delivered_with.append(pid)
                            if tuple[0] not in pkg_to_add_to_truck:
                                pkg_to_add_to_truck.append((tuple[0],0)) # distance TBD in part 6
                                # check if the package to add has collisions
                                has_collision = tuple[0].has_collision()
                                if has_collision:
                                    neighbors = distance_graph.get_adj_list(tuple[0].get_address())
                                    pkgs_at_same_address = neighbors[0]
                                    for _pkg in pkgs_at_same_address:
                                        if _pkg is not tuple[0]:
                                            _delivery_time = calculate_delivery_time(tuple[1])
                                            _delivery_time += current_time
                                            if package_can_be_added_to_truck(_pkg, truck, _delivery_time):
                                                pkg_to_add_to_truck.append((_pkg, 0))
                                            
        
        # 6a. Try adding packages to truck
        # first package in pkg_to_add_to_truck is always going to be the closest_package
        # many times it is the only package to add.
        # other times we have reached either a collision or delivered_with scenario, then there will be >1 package to try to add
        # for the case where there are many packages, we want to find the 'nearest neighbor' for the series of packages. "Sort" the packages in a sequence that allow eachother to find their repsective nearest neighbor in a sequence

        # Create sequence of nearest packages prior to adding to truck stack
        if len(pkg_to_add_to_truck) > 1: # more than one package to add
            p_tuple = pkg_to_add_to_truck[0] # (Package Obj, distance)
            first_pkg = p_tuple[0]
            new_list_to_add_to_truck = [p_tuple]
            visited_packages = [first_pkg]
            # for each nearest package that is to be added, we need to get the edges for THAT package; always the next-nearest. The distance needs to be measured always from the prior package
            new_neighbor_edges = distance_graph.get_adj_list(first_pkg.get_address())

            for i in range(len(pkg_to_add_to_truck)-1): # (-1) to not include the first_pkg that has already been 'added' to new_list_to_add_to_truck
                _closest_package = None
                _closest_distance = None

                # pick the first unvisited available package in the list for a comparison distance
                for tuple in pkg_to_add_to_truck:
                    _pkg = tuple[0]
                    if _pkg not in visited_packages:
                        _closest_package = _pkg
                        for d_tuple in new_neighbor_edges[1:]:
                            if d_tuple[0] == _pkg:
                                _closest_distance = d_tuple[1]
                                break
                        if not _closest_distance:
                            # edge it to itself. Distance is 0
                            _closest_distance = 0 
                
                # compare distances and find the closest pkg
                for tuple in pkg_to_add_to_truck:
                    _pkg = tuple[0]
                    _dist = None
                    if _pkg not in visited_packages and _pkg is not _closest_package:
                        for d_tuple in new_neighbor_edges[1:]:
                            if d_tuple[0] == _pkg:
                                _dist = d_tuple[1]
                                break
                        if not _dist:
                            # edge back to itself
                            _dist = 0
                        if _dist < _closest_distance:
                            _closest_package = _pkg
                            _closest_distance = _dist
                # after all comparison, if there is a _closest_package: add to visited_packages, add tuple to new_list_to_add_to_truck, AND get the list of edges from the distance_graph for the _closest_package to begin another comparison from a different starting point on the graph
                if _closest_package:
                    visited_packages.append(_closest_package)
                    new_list_to_add_to_truck.append((_closest_package, _closest_distance))
                    new_neighbor_edges = distance_graph.get_adj_list(_closest_package.get_address())

            # Assign the sequenced list of packages to add to pkg_to_add_to_truck
            pkg_to_add_to_truck = new_list_to_add_to_truck

        # 6b. Add packages to the truck from sequenced pkg_to_add_to_truck list
        for i, _pkg_tuple in enumerate(pkg_to_add_to_truck):
            package_to_add = _pkg_tuple[0]
            distance_to_the_package_being_added = _pkg_tuple[1]
            # always start by adding the closest to the truck stack. update the time and mileage and set attributes for package
            truck.push(package_to_add)
            current_time += calculate_delivery_time(distance_to_the_package_being_added)
            package_to_add.set_time_delivered(current_time)
            package_to_add.set_time_routed(truck.get_departure_time())

            truck.add_mileage(distance_to_the_package_being_added, current_time)

            if i < (len(pkg_to_add_to_truck)-1): # there are still packages to add to the truck
                # check if truck is full - if it is, we cannot successfully get all the packages on the truck without having to remove previously routed packages.
                # remove this round of packages and set the truck to route immediately - dispite not being full
                if truck.is_full():
                    for j in range(i+1):
                        p = truck.pop()
                        truck.remove_mileage(p.get_time_delivered())
                        p.set_time_delivered(None)
                        p.set_time_routed(None)
                    truck.set_force_route(True)
                    break
            
        # End of Recursion - CHECK IF TRUCK FULL BASE CASE 2 OR TRUCK IS FORCED TO ROUTE BASE CASE 3
        if truck.is_full() or truck.is_force_route():
            last_stop = truck.peek() # top of the stack
            # from the last_stop, get the distance to return back to the hub for more packages
            _adj_lst = distance_graph.get_adj_list(last_stop.get_address())
            for tuple in _adj_lst[1:]:
                package_id = tuple[0].get_package_id()
                if package_id == 0: # HUB id is 0
                    distance_to_hub = tuple[1]
                    # add the time it takes to return to the hub to the "current time"
                    time_to_return_to_hub = calculate_delivery_time(distance_to_hub)
                    time_arriving_at_hub = current_time + time_to_return_to_hub

                    # truck.add_mileage(distance_to_hub, time_arriving_at_hub, no_pkg=True)

                    return (truck, time_arriving_at_hub)            

        # 5. Reaching here, we have not reached any of the base cases. 
        # Continue calling find_nearest_neighbor_path with the {last_stop}, {truck}, and {current_time}
        last_stop = truck.peek()
        truck_and_return_time_tuple = find_nearest_neighbor_path(last_stop, truck, current_time)


        # 6. final result: (Truck Object, time_ariving_at_hub)
        return truck_and_return_time_tuple

########################################################################################
### Nearest Neighbor Wrapper Functions (algo i/o) ######################################
########################################################################################
    def set_up_truck_wrapper(trtt=None, trucks=[]):
        """
        input:
            {optional}[list[tuple]] - list of truck return time tuples (truck, return_time)
             {optional}[list[Truck object]] - list of prepared trucks

        resets trucks between routes from the hub; clears truck stack and sets particular attributes

        verifies that there are still packages at the hub to deliver

        returns a list of trucks prepared for another delivery route

        output: 
            [list[Truck object]] - list of prepared trucks
        """
        prepared_trucks = trucks

        truck_return_time_tuples = trtt # [(Truck, return_time), (Truck, return_time)]
        
        # only set up trucks if there are still packages to deliver that have arrived
        are_unrouted_packages = False
        delayed_arrival = None

        for f_string in package_f_string_list:
            _pkg = daily_hash_table.get(f_string)
            _status = _pkg.get_delivery_status()
            if _status == "at the hub":
                # there are still packages that have not been routed that can be
                if _pkg.is_delayed():
                    arrival = _pkg.get_delayed_arrival()
                    truck_return_times = [t[1] for t in truck_return_time_tuples]
                    for trt in truck_return_times:
                        if arrival < trt:
                            are_unrouted_packages = True
                            break
                        if not delayed_arrival:
                            delayed_arrival = arrival
                        else:
                            if arrival > delayed_arrival:
                                delayed_arrival = arrival
                else:
                    are_unrouted_packages = True
                    break

        if are_unrouted_packages:                                         
            if truck_return_time_tuples:
                for tuple in truck_return_time_tuples:
                    _truck = tuple[0]
                    _time = tuple[1]
                    _truck.clear_packages(_time)
                    _truck.set_departure_time(_time)
                    prepared_trucks.append(_truck)      
        else:
            if delayed_arrival:
                # there are no other packages except for delayed ones and no trucks are back at the hub yet
                if truck_return_time_tuples:
                    for tuple in truck_return_time_tuples:
                        _truck = tuple[0]
                        _time = tuple[1]
                        _truck.clear_packages(delayed_arrival)
                        _truck.set_departure_time(delayed_arrival)
                        prepared_trucks.append(_truck)
            else:
                # there are no more packages at all
                for tuple in truck_return_time_tuples:
                    _truck = tuple[0]
                    _time = tuple[1]
                    _truck.clear_packages(_time)
                    _truck.set_departure_time(delayed_arrival)
                    prepared_trucks.append(_truck)
        # returns NO ready trucks if all packages have been routed that can be
        return prepared_trucks # [Truck, Truck]
    def route_daily_packages_wrapper(prepared_trucks):
        """
        input: [list[Truck object]] - list of prepared trucks

        takes empty prepared trucks and efficently routes packages via find_nearest_neighbor_path(); starting at the hub

        ensures_timely_delivery given the routed package roster from find_nearest_neighbor_path()

        returns the completed routes as a list of tuples; the truck and the time arriving back at hub

        output: [list[tuple]] - list of truck return time tuples (truck, time_returning_to_hub)
        """
        truck_return_time_tuples = []
        ordered_prepared_trucks = []
        for i in range(len(prepared_trucks)):
            first_truck = None
            earliest_departure = None
            for _truck in prepared_trucks:
                if _truck not in ordered_prepared_trucks:

                    _departure_time = _truck.get_departure_time()
                    if not earliest_departure:
                        first_truck = _truck
                        earliest_departure = _departure_time
                        continue

                    if _departure_time < earliest_departure:
                        first_truck = _truck
                        earliest_departure = _departure_time
                        continue
            ordered_prepared_trucks.append(first_truck)
        for _truck in ordered_prepared_trucks:
            _departure_time = _truck.get_departure_time()
            if _departure_time:
                trtt = find_nearest_neighbor_path(hub, _truck, _departure_time) # returns (Truck, time_truck_returns_to_hub)
                truck_return_time_tuples.append(trtt)
        # Truck is full -- or as full as it can be (unrouted restricted packages)
        # check earlies and ensure they are delivered on time
        if truck_return_time_tuples:
            ensure_timely_delivery(truck_return_time_tuples) 

        # set return time/miles back to hub
        for _truck in ordered_prepared_trucks:
            top = _truck.peek()
            if top:
                top_del_time = top.get_time_delivered()
                distance_to_hub = find_distance_between_x_and_y(hub, top)
                time_arriving_at_hub = (calculate_delivery_time(distance_to_hub) + top_del_time)
                _truck.add_mileage(distance_to_hub, time_arriving_at_hub, is_pkg=False)

                for i in range(2):
                    if truck_return_time_tuples[i][0] == _truck:
                        del truck_return_time_tuples[i]
                        truck_return_time_tuples.append((_truck, time_arriving_at_hub))

        # for _tuple in truck_return_time_tuples:
        #     print(f"{_tuple[0]} -- COMPLETED ROUTE -- Return to hub at: {_tuple[1]}")
        #     _tuple[0].print_roster()

        return truck_return_time_tuples 

########################################################################################
### Deliver All Packages Using Nearest Neighbor Algorithm ##############################
########################################################################################

    # Read in the Day's list of packages and addresses to deliver from the excel spreadsheet
    package_data = data.package_file_to_CSV()
    package_f_string_list = package_data[0]
    unique_addresses = package_data[1]
    package_excel_cell_data_matrix = package_data[2]

    # Read in the distance matrix and addresses from the excel spreadsheet - to plan the most efficent routes
    distance_data = data.distance_table_to_CSV()
    distance_matrix = distance_data[0]
    d_addresses = distance_data[1]

    # add the packages to the hash table and graph
    add_packages_to_hashtable_and_graph(package_excel_cell_data_matrix, daily_hash_table, distance_graph)
    update_delivered_with(daily_hash_table,package_f_string_list)

    # add edges between every other delivery address
    add_distance_edges(distance_graph, package_f_string_list)
    
    # assign the hub
    hub = daily_hash_table.get(package_f_string_list[0])
    hub.set_delivery_status("HUB")

    # find package_9 and fix incorrect address
    fix_incorrect_address(9, '10:20 am', '300 State St', 'Salt Lake City', 'UT', 84111)

    # Prepare trucks for first delivery route
    prepared_trucks_with_packages_still_to_deliver = set_up_truck_wrapper(trucks=[truck1,truck2])

    # Routing Trucks - while there are still packages to deliver
    while prepared_trucks_with_packages_still_to_deliver:
        truck_return_time_tuple = route_daily_packages_wrapper(prepared_trucks_with_packages_still_to_deliver)
        prepared_trucks_with_packages_still_to_deliver = set_up_truck_wrapper(trtt=truck_return_time_tuple, trucks=[])

########################################################################################
### Provide interface for user to get info about trucks or packages at any given time ##
########################################################################################

# run main.py in the python interpreter
    while True:
        os.system('cls||clear')
        print("--------------------------------------------------------------------")
        print("|             DATA STRUCTURES AND ALGORITHMS II — C950             |")
        print("|                   TASK 1: WGUPS ROUTING PROGRAM                  |")
        print("|                           Stephen Koch                           |")
        print("|                       Student ID: 001435707                      |")
        print("|__________________________________________________________________|")
        print("\n--Routing Program Interface--")
        print("1. Track a package")
        print("2. Get status of all packages")
        print("3. Get status of all trucks")
        print("4. Get truck package rosters")
        print("5. Exit\n")
        
        response = input("Choose an option: ")

        if response == "1":
            response_one = True
            while response_one:

                getting_package_id = True
                while getting_package_id:
                    package_id = input("\n{type \"exit\" to return} Enter package id: ")

                    if package_id.lower() == "exit":
                        package_id = None
                        response_one = False
                        break
                    try:
                        package_id = int(package_id)
                        if len(package_f_string_list) >= package_id > 0:
                            getting_package_id = False
                        else:
                            print(f"package id is out of range -- {package_id} -- please enter a valid package")
                    except:
                        print(f"invalid package id -- {package_id} -- please enter integer only")

                if package_id:
                    getting_time = True
                    while getting_time:
                        time = input("Enter time in the 24-hour format \"xx:xx\": ")
                        try:
                            time_idx = time.index(':')
                            if time_idx > 1: # xx:xx
                                d_line = time[(time_idx-2):(time_idx+3)]
                            else: # x:xx
                                d_line = time[(time_idx-1):(time_idx+3)]
                            if len(d_line) == 5:
                                hours = int(d_line[0:2])
                                minutes = int(d_line[3:5])
                            else:
                                hours = int(d_line[:1])
                                minutes = int(d_line[2:4])
                            time = (hours*60) + minutes
                            getting_time = False
                        except:
                            print(f"invalid format -- {time} -- please input time in the 24-hour format: \"xx:xx\"")

                    for f in package_f_string_list[1:]:
                        p = daily_hash_table.get(f)
                        pid = p.get_package_id()
                        if pid == int(package_id):
                            p.print_status_and_info_at_given_time(time)
                    

        if response == "2":
            getting_time = True
            while getting_time:
                time = input("\nEnter time in the 24-hour format \"xx:xx\": ")
                try:
                    time_idx = time.index(':')
                    if time_idx > 1: # xx:xx
                        d_line = time[(time_idx-2):(time_idx+3)]
                    else: # x:xx
                        d_line = time[(time_idx-1):(time_idx+3)]
                    if len(d_line) == 5:
                        hours = int(d_line[0:2])
                        minutes = int(d_line[3:5])
                    else:
                        hours = int(d_line[:1])
                        minutes = int(d_line[2:4])
                    time = (hours*60) + minutes
                    getting_time = False
                except:
                    print(f"invalid format -- {time} -- please input time in the 24-hour format: \"xx:xx\"")

            print("\n____Status_of_All_Packages____")
            for f in package_f_string_list:
                p = daily_hash_table.get(f)
                if p is not hub:
                    p.print_status_and_info_at_given_time(time)
          
            wait = input("\npress any key to continue")

        if response == "3":
            getting_time = True
            while getting_time:
                time = input("\nEnter time in the 24-hour format \"xx:xx\": ")
                try:
                    time_idx = time.index(':')
                    if time_idx > 1: # xx:xx
                        d_line = time[(time_idx-2):(time_idx+3)]
                    else: # x:xx
                        d_line = time[(time_idx-1):(time_idx+3)]
                    if len(d_line) == 5:
                        hours = int(d_line[0:2])
                        minutes = int(d_line[3:5])
                    else:
                        hours = int(d_line[:1])
                        minutes = int(d_line[2:4])
                    time = (hours*60) + minutes
                    getting_time = False
                except:
                    print(f"invalid format -- {time} -- please input time in the 24-hour format: \"xx:xx\"")

            truck1_miles = truck1.get_mileage_at_time(time)
            truck2_miles = truck2.get_mileage_at_time(time)
            
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

            if truck1_miles:
                truck1_miles = round(truck1_miles,2)
            if truck2_miles:
                truck2_miles = round(truck2_miles,2)

            truck1_packages_delivered = truck1.get_packages_delivered_at_miles(truck1_miles)
            truck2_packages_delivered = truck2.get_packages_delivered_at_miles(truck2_miles)


            print("\n____Status_of_All_Trucks____")
            print(f"\n({time_str}) Truck 1 -- Daily Miles: {truck1_miles} -- Packages Delivered: {truck1_packages_delivered}")
            print(f"\n({time_str}) Truck 2 -- Daily Miles: {truck2_miles} -- Packages Delivered: {truck2_packages_delivered}")

            wait = input("\npress any key to continue")

        if response == "4":
            finding_truck = True
            
            while finding_truck:
                truck_response = input("\nTruck number: ")
                if truck_response == "1":
                    truck1.print_roster()
                    break
                if truck_response == "2":
                    truck2.print_roster()
                    break
                print(f"invalid truck -- {truck_response} -- please input a valid truck number")

            wait = input("\npress any key to continue")
                  
        if response == "5":
            os.system('cls||clear')
            break

 