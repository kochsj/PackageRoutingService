class Graph:
    """
    Graph data structure; holds vertices and edges
    
    Parameters:
        {optional} [int] - length of adj_list
    """
    def __init__(self, length=1024):
        self._length_of_adj_list = length
        self._adj_list = [None] * self._length_of_adj_list
    
    def __repr__(self):
        return "Distance Graph"

    def add_package(self, package):
        """
        input: [Package object]

        adds package to hashtable; handles collisions at the same hash index

        output: None
        """
        u_address = package.get_address()
        _hash_index = self._hash(u_address)

        if self._adj_list[_hash_index]: 
            # something is at the hash_index. collision has happened
            # reference the first package and set_collision=True and append the new package
            first_pkg = self._adj_list[_hash_index][0][0]
            if not first_pkg.has_collision():
                first_pkg.set_collision(True)
            package.set_collision(True)
            self._adj_list[_hash_index][0].append(package)
        else: 
            self._adj_list[_hash_index] = [[package]]

    def add_edge(self, start_vertex, end_vertex, distance=0):
        """
        input: 
            [Package object] - starting_package,
             [Package object] - ending_package, 
            {optional}[float] - distance

        adds package to hashtable; handles collisions at the same hash index

        output: None
        """
        start_vertex_u_address = start_vertex.get_address()
        _start_hash_index = self._hash(start_vertex_u_address)

        if not self._adj_list[_start_hash_index]: # nothing at that index
            raise KeyError(f'{_start_hash_index}-{start_vertex_u_address} not in {self}')

        adj_list = self._adj_list[_start_hash_index] #[vertex, (vertex, dist), (vertex, dist), etc...]

        if distance:
            if (end_vertex, distance) not in adj_list:
                adj_list.append((end_vertex, distance))

    def get_adj_list(self, u_address):
        """
        Gets the neighboring vertices to a given vertex
        Parameters:
            [string] - package address
        Return:
            [list] - list of vertices with weights
        """
        _hash_index = self._hash(u_address)
        
        try:
            return self._adj_list[_hash_index]
        except:
            return []

    def _hash(self, key):
        """
        Takes key as arguement
        Returns hash-index
        """
        #add ascii values of char together
        sum_chars = 1
        for char in key: 
            sum_chars += ord(str(char))
        #Square the sum
        square_sum = sum_chars**2
        #Floor devide by the first ascii value in key
        divide_square = square_sum // ord(key[0])
        #Mod length of hash table and return
        return (divide_square % self._length_of_adj_list)
