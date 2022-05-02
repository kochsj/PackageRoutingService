# PackageRoutingService
CLI App for calculating most efficient package routes. Manifest is read from file into recursive nearest 
neighbor algorithm.

Manifest file and distance data are found in <b>data/</b>

To use the CLI app, clone and navigate to the PackageRoutingService directory. Run <b>main.py</b> with your python interpreter:

```% python3 main.py```

Features include:
1. Track a package
2. Get status of all packages
3. Get status of all trucks
4. Get truck package roster

Follow prompts in the terminal. 

# Scope / Problem Domain
    # Salt Lake City DLD route has:
    trucks = 3
    drivers = 2
    avg_deliveries_per_day = 40

    # Specific package requirements (vary by package individually):
    • delivery deadline
    • required to be on specific truck
    • delay / arrival time to depot
    • wrong address listed 
    • must be delivered with other specific packages
    
    # Specific truck requirements
    • combined total distance for each truck <= 140miles
    • trucks leave the depot at 8am


# Self-Adjusting Algorithim
    My self adjusting algorithim that I am using I will call a "Nearest Neighbor" algorithim. The core of my package 
    routing algorithim is the piece where after every package is delivered, the function will check for the nearest 
    "next" delivery location. It is my belief that this algorithm will, in all cases, be the most efficent to deliver 
    packages in the fewest miles and stops possible. 
    
    The algorithim will start with the package with the earliest delivery deadline that is closest to the depot. 
    Then it will:
        1) Check what the time will be when the driver reaches that first stop. Keep track of the time.
        2) IF there are still deadline packages AND not curently on route to deadline package... Check the list 
           of delivery deadlines for the next delivery(s) (>=) the current deadline being met.
            2a) Find the next closest in miles. Save reference to this address. This is the target.
        3) Find the next closest stop to that location in miles...
            3a) that can fit on the truck for delivery
            3b) that is still on the packages to assign list
            3c) (IF deadline package exists): that results in driver being closer to target location
                - AND does NOT make the deadline package late
                3c.a) IF it makes the deadline package LATE:
                    - Try to put deadline package as the first stop for another route 
                    3c.b) If there are no more valid routes to assign this package too
                        - Head straight to the target deadline location (skipping all other "next closest")
                            3c.c) IF the package is still late:
                                - Move back a step to the previous package...
                                    -- IF it is not a 'deadline' package: REMOVE it from the route queue
                                    -- IF it is a 'deadline' package: There is no possible way to get the package there 
                                       on time. NO_MORE_ROUTES(3c.b) && cannot make the other deadline package late by 
                                       moving another in its place.
                                - Recalculate the time that the deadline package will be delivered at
                                - repeat 3c.c
        4) Assign this 'next' package to the route
        5) Remove the 'next' package from the list of packages to assign
        6) Update the 'current time'. 
        7) Set the delivery_satus to "delivered" and record the 'current_time'.
        8) Add milage to total_miles_travled.
        9) Repeat steps 2-8

# Original ALGO:
    I set out to create an algorithm for my program to route packages. I started with writing down some details about WGUPS,
    requirements for packages, and known assumptions provided in the problem domain.
    
    Those packages that have deadlines to meet are the first priority and should be out on the first truck at 8am if at all
    possible. Packages that are arriving late but also have deadlines need to be out as soon as they arrive (@ 9:05am). 
    Packages that need to be on specific trucks or that are being delivered to the same address need to be checked when adding 
    these 'deadline' packages to trucks. If a 'deadline' package has other packages that are going to the same address - 
    those other packages should be prioritized to be added with the 'deadline' package to avoid going to the same address
    twice. Also if the 'deadline' package itself needs to be on a specific truck, that needs to be taken into considerstion 
    when planning the routes. 
    
    Every route should start with the closest distance and nearest 'deadline' package then proceed 'away' from the depot 
    toward the next nearest package destination again and again. As for the package(s) with incorrect addresses or that arrive 
    late, we need to check if the packages have deadlines first. If they do, we need to ensure that they leave as close to 
    the same time as they arrive at the depot. Otherwise, if there are no deadlines to meet, they can go out later in the 
    day after the 'deadline' priority packages are delivered.

    The original algorithm that I wrote out below, is written in human sentences to get these ideas out into the markdown file. 
    Next I will be determining what data structure(s) I will be using for my packages, routes, and distances and writing the 
    algorithm in a more pseudo code format.
    

     1. Check if any trucks need to leave at a later time - Are there late arrivals of packages that ALSO have time deadlines(?)
         if late arrivals do not have any deadlines, no action needed at this time
     2. Create "packages" for the day's packages coming in. Including a unique ID, address, delivery deadline, mass(kilo), and 
        special notes
     3. Pull out packages with wrong address (wrong_address_set)
     4. Pull out packages that must be delivered on same truck / delivered with specific packages (same_truck_set)
     5. Create sets for every address and add to set. Not including wrong address set items. (set_of_all_addresses) (<=n sets)
     6. Check if any sets contain earlies
         if they do - check if any package in the set with an early contain a late ex:{123_main_street_set:(E, EOD, EOD, L)}
             if it does - remove the late package to the late set (late_set) ex:{now 123_main_street_set:(E, EOD, EOD)}
         add set to early set
     7. Now we can create "routes" using data from our package sets
     8. Start with the earliest delivery deadline. That always goes on the first truck out.
         - if there are multiple at the earliest deadline, start with the closest to the depot.
             - then go to the next closest to the previous (miles). Repeat.
         Group packages, regardless of deadline, that are going to the SAME address, or need to be on same truck
             **** keep track of these "bundled" packages temporarily. They may need to be removed in step 10. ****
         Keep track of the estimated time (@ 18mph avg)
     9. Continue adding the next closest and next earliest to the first truck (keeping track of time and deadline)
         - if all earlies can fit on it, great!
         - if not, then some earlies will need to be worked onto the 'next' truck
             - repeating steps 8 and 9 for the 'next' truck
     10. Ensure all 'earlies' will be ariving on time. If not, that means we have run out of drivers, space in trucks, or time.
         - look to the current trucks that have "bundled" packages. Remove the 'farthest' eod bundle and add the 'nearest' early.
             repeat untill all EOD "bundles" are replaced
                 should be enough room for all the earlies
                     if not there is nothing that can be done ( trucks are already filled with earlies in the "nearest" pattern; 
                     filled most optimally; and there are no more routes available )
     11. Trucks return to depot and are reloaded. Repeat steps 8 and 9 
     12. Make sure that packages are removed from the set as they are assigned, so to always know the closest to depot
     13. At this point the routes should be sorted. Do a check that no route is over 140miles.
         if it is not, Great!
         if it is - we need to fix that. Remove routes from over-assigned truck until under 140miles. Add those packages to the 
         next truck. Repeat step 13 for all trucks
        
        Data Structures (v.1)
        Array of strings from package file:
            list_of_packages[40] = ["1,195 W Oakland Ave,Salt Lake City,UT,84115,10:30 AM,21,", "2,2530 S 500 E, Salt Lake..", etc.]
            "package 1" is the package located at list_of_packages[0].

        Package Class Objects
            Package() - attributes: id, address, deadline, city, zipcode, weight, delivery status, delivery time, special notes
            Getters and setters
                especially for delivery status and delivery time
        
        D. STORING PACKAGE DATA: Hash Table of unique keys and Package(s) as values
            buckets contain the Package
            colisions are managed via linked list at shared index

        A. DELIVERING PACKAGES: Graph of addresses and edges for distance in miles
            "address 1" is "package 1" - hashed and stored in the Hash Table
            There are 27 verticies
            Each vertex has 26 edges... 
            Thats 351 edges if we half it because they repeat to eachother. 702 using an adj matrix
                _adj_list = {[address_one, (address_two, 7.2), (address_three, 3.8), ...], [address_two, (address_one, 7.2), 
                (address_three, 7.1), ...], ...}
                a given edge to a given address node has the distance at the_tuple[1]
                    - ex_tuple = (address_two, 7.2) ---> ex_tuple[1] = 7.2 (miles)
                    - find "current node", for edge in len(current_node) find the shortest distance and index of tuple with shortest 
                      distance. Then:
                        - curent_node[shortest_index] = (shortest_dist_address, shortest_dist_miles)

            Thoughts:
            - maybe when we are adding the edges we can sort them in assending order at that point. Then the only check needs to be: 
              grab the first edge, CHECK if the end_address has already been delivered to, if so, grab the next edge, repeat untill 
              you have the closest edge that has not been delivered to.
            - instead of looping through the entire array every single time to ensure that we have the shortest distance that has also 
              not been delivered to... (O(n^2))

