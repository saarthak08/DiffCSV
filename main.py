import os
import shutil
import csv

from flask import flash, request, redirect, render_template, session, send_file, Blueprint

from werkzeug.utils import secure_filename

main_api = Blueprint('main_api', __name__)

from app import app

ALLOWED_EXTENSIONS = set(['csv'])

filenames = []

cnp = "COLUMN NOT PRESENT"
enp = "ENTRY NOT PRESENT"
ep = "ENTRY PRESENT"

def recreate_dir():
    if os.path.exists(app.config['FILES_FOLDER']):
        shutil.rmtree(app.config['FILES_FOLDER'])
        os.mkdir(app.config['FILES_FOLDER'])
    else:
        os.mkdir(app.config['FILES_FOLDER'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def compare_filenames(files):
    return files[0].rsplit('.', 1)[1].lower() == files[1].rsplit('.', 1)[1].lower()


@main_api.route('/download', methods=['POST', 'GET'])
def download_file():
    try:
        return send_file(app.config['FILES_FOLDER'] + '/result.csv', attachment_filename='result.csv',
                         as_attachment=True, cache_timeout=0)
    except FileNotFoundError:
        flash('\'result.csv\' file not found at ' + app.config['FILES_FOLDER'])
        return redirect('/')


@main_api.route('/')
def upload_form():
    return render_template('upload.html')


@main_api.route('/', methods=['POST'])
def upload_file():
    global filenames

    filenames = []

    if request.method == 'POST':

        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        if files is not None:
            i = 1
            for file in files:

                if file.filename == '':
                    flash('No file selected for uploading.')
                    filenames = []
                    return redirect(request.url)

                if not (file and allowed_file(file.filename)):
                    filenames = []
                    flash('Allowed file type is csv only.')
                    return redirect(request.url)

                filename = 'input(' + str(i) + ')-' + secure_filename(file.filename)
                filenames.append(filename)
                i += 1

            if len(filenames) == 2 and compare_filenames(filenames):
                recreate_dir()

                i = 0
                for file in files:
                    file.save(os.path.join(app.config['FILES_FOLDER'], filenames[i]))
                    i += 1

                flash('Files successfully uploaded at ' + app.config['FILES_FOLDER'])
                return redirect('/')

            else:
                filenames = []
                flash('Both file extensions should be same.')
                return redirect('/')


@main_api.route('/compare', methods=['GET', 'POST'])
def comp_file():
    os.chdir(app.config['FILES_FOLDER'])
    global filenames

    if (len(filenames) != 0) and len(filenames) == 2:

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

        # Primary key column number in input file 1
        primary_index_first = app.config["PRIMARY_KEY_FIRST"]

        # Primary key column number in input file 2
        primary_index_second = app.config["PRIMARY_KEY_SECOND"]

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
                            if column == primary_index_first:
                                # Adding primary key for comparison
                                primary_index_one = row[column]
                            else:
                                # Columns names in first csv file stored in an array and set respectively
                                file_one_columns_array.append(row[column])
                                file_one_columns_set.add(row[column])
                    # Condition if row isn't the first one (i.e. entry rows)
                    else:
                        # id (primary key) added to id set of first input file
                        file_one_id_set.add(row[primary_index_first])
                        # initialised a temporary dictionary
                        temp_dict = {}
                        # Reading each column of row
                        for column in range(len(row)):
                            # Checking if the column is not the id column
                            if column != primary_index_first:
                                # Adding the entries to the temporary dictionary where key is the column name and value is the value of the column
                                temp_dict[file_one_columns_array[column - 1]] = row[column]
                        # Adding the temporary dictionary to the dictionary of file one as nested dictionary where key is the value of id and value is the temporary dictionary
                        file_one_dictionary[row[primary_index_first]] = temp_dict
                    i += 1
        except FileNotFoundError:
            print("Error! `input(1)` not present in the upload directory.")
            flash("Error! `input(1)` not present in the upload directory")
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
                            if column == primary_index_second:
                                # Adding primary key for comparison
                                primary_index_two = row[column]
                            else:
                                # Columns names in second csv file stored in an array and set respectively
                                file_two_columns_set.add(row[column])
                                file_two_columns_array.append(row[column])
                    # Condition if row isn't the first one (i.e. entry rows)
                    else:
                        # id (primary key) added to id set of second input file
                        file_two_id_set.add(row[primary_index_second])
                        # initialised a temporary dictionary
                        temp_dict = {}
                        # Reading each column of row
                        for column in range(len(row)):
                            # Checking if the column is not the id column
                            if column != primary_index_second:
                                # Adding the entries to the temporary dictionary where key is the column name and value is the value of the column
                                temp_dict[file_two_columns_array[column - 1]] = row[column]
                        # Adding the temporary dictionary to the dictionary of file two as nested dictionary where key is the value of id and value is the temporary dictionary
                        file_two_dictionary[row[primary_index_second]] = temp_dict
                    i += 1
        except FileNotFoundError:
            print("Error! `input(2)` not present in the upload directory.")
            flash("Error! `input(2)` not present in the upload directory.")
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
        out_file = open('result.'+filenames[0].rsplit('.', 1)[1].lower(), 'w')

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
                                out_file.write("," + cnp)
                        # Write the differences
                        out_file.write("\n INPUT-2 ," + temp_id + ",")
                        out_file.write(file_two_dictionary.get(temp_id).get(temp_column) + " (" + temp_column + ")")
                        # Iterating each column in all columns to write each value of the column
                        for col in total_columns:
                            # Checking if the column is present in second input file
                            if file_two_columns_set.__contains__(col):
                                out_file.write("," + file_two_dictionary.get(temp_id).get(col))
                            else:
                                out_file.write("," + cnp)
                        out_file.write("\n")
                out_file.write("\n")

            # If the id is present in first input file and not present in second input file
            elif file_one_id_set.__contains__(temp_id) and (not file_two_id_set.__contains__(temp_id)):
                # Write the differences
                out_file.write(" INPUT-1 ," + temp_id + ",")
                out_file.write(ep)
                # Iterating each column in all columns to write each value of the column
                for col in total_columns:
                    # Checking if the column is present in first input file
                    if file_one_columns_set.__contains__(col):
                        out_file.write("," + file_one_dictionary.get(temp_id).get(col))
                    else:
                        out_file.write("," + cnp)
                # Write the differences
                out_file.write("\n INPUT-2 ," + temp_id + ",")
                out_file.write(enp)
                # Iterating each column in all columns to write each value of the column
                for col in total_columns:
                    # Checking if the column is present in second input file
                    if file_two_columns_set.__contains__(col):
                        out_file.write("," + enp)
                    else:
                        out_file.write("," + cnp)
                out_file.write("\n\n")

            # If the id is not present in first input file and present in second input file
            elif (not file_one_id_set.__contains__(temp_id)) and file_two_id_set.__contains__(temp_id):
                # Write the differences
                out_file.write(" INPUT-1 ," + temp_id + ",")
                out_file.write(enp)
                # Iterating each column in all columns to write each value of the column
                for col in total_columns:
                    # Checking if the column is present in first input file
                    if file_one_columns_set.__contains__(col):
                        out_file.write("," + enp)
                    else:
                        out_file.write("," + cnp)
                # Write the differences
                out_file.write("\n INPUT-2 ," + temp_id + ",")
                out_file.write(ep)
                # Iterating each column in all columns to write each value of the column
                for col in total_columns:
                    # Checking if the column is present in second input file
                    if file_two_columns_set.__contains__(col):
                        out_file.write("," + file_two_dictionary.get(temp_id).get(col))
                    else:
                        out_file.write("," + cnp)
                out_file.write("\n\n")

        if len(filenames) == 2:
            flash('Files compared successfully.\n The \'result.csv\' file is stored at \"' +
                  app.config['FILES_FOLDER'] + '\".')
            session['filenames'] = None

    else:
        flash('Please upload the files first!')
        session['filenames'] = None

    return redirect('/')
