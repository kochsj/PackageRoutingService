import xlrd
import math

def package_file_to_CSV():
    """
    input: None

    reads the package file from excel and creates three lists of data from the sheet

    output: tuple:(f_string_list, address_list, cell_data_list)
    """
    package_file = xlrd.open_workbook('data/WGUPS Package File.xls').sheet_by_name('Sheet1')
    package_f_string_list = ["0,4001 South 700 East,Salt Lake City,UT,84107,,,"]
    package_excel_cell_data_matrix = [["0,4001 South 700 East,Salt Lake City,UT,84107,,,",0,"4001 South 700 East","Salt Lake City","UT",84107,"EOD",0,'']]
    unique_addresses = ["4001 South 700 East"]
    num_rows = package_file.nrows
    current_row = 8 #0-indexed, so "row 9" in excel is actually row#8 here
    while current_row < num_rows:
            row_data = package_file.row(current_row) # list

            package_id = math.floor(row_data[0].value)
            address = row_data[1].value
            city = row_data[2].value
            state = row_data[3].value
            zip = math.floor(row_data[4].value)
            deadline = "EOD"
            if row_data[5].value != "EOD":
                total_minutes = math.floor(row_data[5].value * 1440) #number of minutes in a day
                minutes = total_minutes % 60
                hours = math.floor(((total_minutes - minutes) / 60))
                if minutes == 0:
                    minutes = "00"
                deadline = f'{hours}:{minutes} AM'
            weight = math.floor(row_data[6].value)
            special_notes = row_data[7].value

            f_string = f'{package_id},{address},{city},{state},{zip},{deadline},{weight},{special_notes}'
            package_excel_cell_data_matrix.append([f_string, package_id, address, city, state, zip, deadline, weight, special_notes])


            if address not in unique_addresses:
                unique_addresses.append(address)
            package_f_string_list.append(f_string)

            current_row += 1
    return (package_f_string_list,unique_addresses, package_excel_cell_data_matrix)

def distance_table_to_CSV():
    """
    input: None

    reads the distance table from excel; creates a 2D matrix of cell data and list of distance table addresses

    output: tuple:(distance_matrix(float), address_list(string))
    """
    distance_table = xlrd.open_workbook('data/WGUPS Distance Table.xls').sheet_by_name('Sheet1')
    num_column = distance_table.ncols #29
    num_row = distance_table.nrows #35

    address_row = distance_table.row(7)
    address_list = [ads.value for ads in address_row[2:num_column]]
    
    current_column = 2 # this is WGU; starting HUB
    current_row = 8 #this is WGU; starting HUB for distances
    matrix = []

    while current_row < num_row:
        list_to_append = []

        for i in range(len(matrix)): # fills rows (top-down)
            list_to_append.append(matrix[i][current_row-8])
    
        column_data = distance_table.col(current_column)
        distance_list = [round(dst.value,1) for dst in column_data[current_row:num_row]]

        for distance in distance_list: # fills columns (left-right)
            list_to_append.append(distance)

        matrix.append(list_to_append)

        current_column += 1
        current_row += 1
        
        # print(matrix[current_column-3])
    return (matrix, address_list)
