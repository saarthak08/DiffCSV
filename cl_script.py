import os
import fileinput
import csv

# Filenames with path
filenames = ["files/Inputs/input(1).csv", "files/Inputs/input(2).csv", "files/Output/Diff_01_02.csv"]


def create_dir():
    # Get current directory
    cwd = os.getcwd()

    # Initialising folders
    files_folder = os.path.join(cwd, 'files')
    input_folder = os.path.join(files_folder, 'Inputs')
    output_folder = os.path.join(files_folder, 'Output')

    # If directories don't exist, create them
    if not os.path.exists(files_folder):
        os.mkdir(files_folder)
        os.mkdir(input_folder)
        os.mkdir(output_folder)
    else:
        if not os.path.exists(input_folder):
            os.mkdir(input_folder)
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)


def main():
    create_dir()

    # Declaring the sets of ids (primary index) of input files
    file_one_id_set = set()
    file_two_id_set = set()

    # Declaring the nested dictionaries of input files
    file_one_dictionary = {}
    file_two_dictionary = {}

    # Declaring the sets of columns of input files
    file_one_columns_set = set()
    file_two_columns_set = set()

    # Declaring the set of total columns including columns of both input files.
    total_columns = set()

    # Declaring the set of total ids including ids of both input files.
    total_ids = set()

    # Declaring the set of columns which are common between the two input files.
    columns_intersection = set()

    # Declaring the column name of primary key of input file 1
    primary_index_one = ""

    # Declaring the column name of primary key of input file 2
    primary_index_two = ""

    # Declaring the array of columns of each input file
    file_one_columns_array = []
    file_two_columns_array = []

    try:
        # Opened first input csv file
        with open(filenames[0]) as csv_one:
            # csv reader initialised
            csv_reader_one = csv.reader(csv_one)
            i = 0
            # reading row by row
            for row in csv_reader_one:
                # Checking condition for first row which contains column names
                if i == 0:
                    # Reading each column of row
                    for column in range(len(row)):
                        # Checking for primary key column name
                        if column == 0:
                            # Adding primary key for comparison
                            primary_index_one = row[column]
                        else:
                            # Columns names in first csv file stored in an array and set respectively
                            file_one_columns_array.append(row[column])
                            file_one_columns_set.add(row[column])
                # Condition if row isn't the first one (i.e. entry rows)
                else:
                    # id (primary key) added to id set of first input file
                    file_one_id_set.add(row[0])
                    # initialised a temporary dictionary
                    temp_dict = {}
                    # Reading each column of row
                    for column in range(len(row)):
                        # Checking if the column is not the id column
                        if column != 0:
                            # Adding the entries to the temporary dictionary where key is the column name and value is the value of the column
                            temp_dict[file_one_columns_array[column - 1]] = row[column]
                    # Adding the temporary dictionary to the dictionary of file one as nested dictionary where key is the value of id and value is the temporary dictionary
                    file_one_dictionary[row[0]] = temp_dict
                i += 1
    except FileNotFoundError:
        print("Error! `input(1).csv` not present in `files/Inputs` in folder in the project directory.")
        exit(0)

    try:
        # Opened second input csv file
        with open(filenames[1]) as csv_two:
            # csv reader initialised
            csv_reader_two = csv.reader(csv_two)
            i = 0
            # reading row by row
            for row in csv_reader_two:
                # Checking condition for first row which contains column names
                if i == 0:
                    # Reading each column of row
                    for column in range(len(row)):
                        # Checking for primary key column name
                        if column == 0:
                            # Adding primary key for comparison
                            primary_index_two = row[column]
                        else:
                            # Columns names in second csv file stored in an array and set respectively
                            file_two_columns_set.add(row[column])
                            file_two_columns_array.append(row[column])
                # Condition if row isn't the first one (i.e. entry rows)
                else:
                    # id (primary key) added to id set of second input file
                    file_two_id_set.add(row[0])
                    # initialised a temporary dictionary
                    temp_dict = {}
                    # Reading each column of row
                    for column in range(len(row)):
                        # Checking if the column is not the id column
                        if column != 0:
                            # Adding the entries to the temporary dictionary where key is the column name and value is the value of the column
                            temp_dict[file_two_columns_array[column - 1]] = row[column]
                    # Adding the temporary dictionary to the dictionary of file two as nested dictionary where key is the value of id and value is the temporary dictionary
                    file_two_dictionary[row[0]] = temp_dict
                i += 1
    except FileNotFoundError:
        print("Error! `input(2).csv` not present in `files/Inputs` in folder in the project directory.")
        exit(0)

    # Total columns = Union( 'Columns of input(1)' & 'Column of input(2)' )
    total_columns = file_one_columns_set.union(file_two_columns_set)

    # Total ids = Union( 'ids of input(1)' & 'ids of input(2)' )
    total_ids = file_one_id_set.union(file_two_id_set)

    # Convert set of total ids into array and sort them
    total_ids_array = sorted(total_ids)
    total_ids_array = list(map(int, total_ids_array))
    total_ids_array.sort()
    total_ids_array = list(map(str, total_ids_array))

    # Intersection of the Columns of Input-1 and Columns of Input-2
    columns_intersection = file_one_columns_set.intersection(file_two_columns_set)

    # Opening output result file
    out_file = open(filenames[2], 'w')

    # Adding the `Input File` and `Differences` columns
    out_file.write(" Input File ," + "   " + primary_index_one + "   ,    Differences (COLUMN_NAME)    ")

    # Writing all the heading columns or columns name in the output file
    for col in total_columns:
        out_file.write("," + col)

    out_file.write("\n")
    # Iterating each id from total ids
    for temp_id in total_ids_array:

        # If the id in both files input-1 and input-2
        if file_one_id_set.__contains__(temp_id) and file_two_id_set.__contains__(temp_id):

            # Checking the common columns in both the files for each id
            for temp_column in columns_intersection:

                # If the values of the column do not match
                if file_one_dictionary.get(temp_id).get(temp_column) != file_two_dictionary.get(temp_id).get(
                        temp_column):

                    # Write the differences
                    out_file.write(" INPUT-1 ," + temp_id + ",")
                    out_file.write(file_one_dictionary.get(temp_id).get(temp_column) + " (" + temp_column + ")")

                    # Iterating each column in all columns to write each value of the column
                    for col in total_columns:

                        # Checking if the column is present in first input file
                        if file_one_columns_set.__contains__(col):
                            out_file.write("," + file_one_dictionary.get(temp_id).get(col))
                        else:
                            out_file.write(", COLUMN NOT PRESENT ")
                    # Write the differences
                    out_file.write("\n INPUT-2 ," + temp_id + ",")
                    out_file.write(file_two_dictionary.get(temp_id).get(temp_column) + " (" + temp_column + ")")
                    # Iterating each column in all columns to write each value of the column
                    for col in total_columns:
                        # Checking if the column is present in second input file
                        if file_two_columns_set.__contains__(col):
                            out_file.write("," + file_two_dictionary.get(temp_id).get(col))
                        else:
                            out_file.write(", COLUMN NOT PRESENT ")
                    out_file.write("\n")
            out_file.write("\n")

        # If the id is present in first input file and not present in second input file
        elif file_one_id_set.__contains__(temp_id) and (not file_two_id_set.__contains__(temp_id)):
            # Write the differences
            out_file.write(" INPUT-1 ," + temp_id + ",")
            out_file.write(" ENTRY PRESENT ")
            # Iterating each column in all columns to write each value of the column
            for col in total_columns:
                # Checking if the column is present in first input file
                if file_one_columns_set.__contains__(col):
                    out_file.write("," + file_one_dictionary.get(temp_id).get(col))
                else:
                    out_file.write(", COLUMN NOT PRESENT ")
            # Write the differences
            out_file.write("\n INPUT-2 ," + temp_id + ",")
            out_file.write(" ENTRY NOT PRESENT")
            # Iterating each column in all columns to write each value of the column
            for col in total_columns:
                # Checking if the column is present in second input file
                if file_two_columns_set.__contains__(col):
                    out_file.write(", ENTRY NOT PRESENT")
                else:
                    out_file.write(", COLUMN NOT PRESENT ")
            out_file.write("\n\n")

        # If the id is not present in first input file and present in second input file
        elif (not file_one_id_set.__contains__(temp_id)) and file_two_id_set.__contains__(temp_id):
            # Write the differences
            out_file.write(" INPUT-1 ," + temp_id + ",")
            out_file.write(" ENTRY NOT PRESENT ")
            # Iterating each column in all columns to write each value of the column
            for col in total_columns:
                # Checking if the column is present in first input file
                if file_one_columns_set.__contains__(col):
                    out_file.write(", ENTRY NOT PRESENT")
                else:
                    out_file.write(", COLUMN NOT PRESENT ")
            # Write the differences
            out_file.write("\n INPUT-2 ," + temp_id + ",")
            out_file.write(" ENTRY PRESENT")
            # Iterating each column in all columns to write each value of the column
            for col in total_columns:
                # Checking if the column is present in second input file
                if file_two_columns_set.__contains__(col):
                    out_file.write("," + file_two_dictionary.get(temp_id).get(col))
                else:
                    out_file.write(", COLUMN NOT PRESENT ")
            out_file.write("\n\n")

    # Output done
    print("Output done! The output file is stored at `files/Output` in the project directory.")


if __name__ == "__main__":
    main()
