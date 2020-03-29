import os
import shutil

from app import app

from flask import flash, request, redirect, render_template, session, send_file

from werkzeug.utils import secure_filename

import csv

ALLOWED_EXTENSIONS = set(['csv'])

filenames = []


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


@app.route('/download', methods=['POST', 'GET'])
def download_file():
    try:
        return send_file(app.config['FILES_FOLDER'] + '/result.csv', attachment_filename='result.csv',
                         as_attachment=True, cache_timeout=0)
    except:
        flash('result.csv file not found at ' + app.config['FILES_FOLDER'])
        return redirect('/')


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
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


@app.route('/compare', methods=['GET', 'POST'])
def comp_file():
    os.chdir(app.config['FILES_FOLDER'])
    global filenames

    if (len(filenames) != 0) and len(filenames) == 2:

        t1 = open(filenames[0], 'r')

        t2 = open(filenames[1], 'r')

        file_one = t1.readlines()

        file_two = t2.readlines()

        t1.close()

        t2.close()

        out_file = open('result.' + filenames[0].rsplit('.', 1)[1].lower(), 'w')

        file_one_id_set = set()
        file_two_id_set = set()
        file_one_dictionary = {}
        file_two_dictionary = {}
        file_one_columns_set = set()
        file_two_columns_set = set()
        total_columns = set()
        total_ids = set()
        columns_intersection = set()
        primary_index_one = ""
        primary_index_two = ""
        file_one_columns_array = []
        file_two_columns_array = []

        with open(filenames[0]) as csv_one:
            csv_reader_one = csv.reader(csv_one)
            i = 0
            for row in csv_reader_one:
                if i == 0:
                    for column in range(len(row)):
                        if column == 0:
                            primary_index_one = row[column]
                        else:
                            file_one_columns_array.append(row[column])
                            file_one_columns_set.add(row[column])
                else:
                    file_one_id_set.add(row[0])
                    temp_dict = {}
                    for column in range(len(row)):
                        if column != 0:
                            temp_dict[file_one_columns_array[column-1]] = row[column]
                    file_one_dictionary[row[0]] = temp_dict
                i += 1

        with open(filenames[1]) as csv_two:
            csv_reader_two = csv.reader(csv_two)
            i = 0
            for row in csv_reader_two:
                if i == 0:
                    for column in range(len(row)):
                        if column == 0:
                            primary_index_two = row[column]
                        else:
                            file_two_columns_set.add(row[column])
                            file_two_columns_array.append(row[column])
                else:
                    file_two_id_set.add(row[0])
                temp_dict = {}
                for column in range(len(row)):
                    if column != 0:
                        temp_dict[file_two_columns_array[column - 1]] = row[column]
                file_two_dictionary[row[0]] = temp_dict
                i += 1

        total_columns = file_one_columns_set.union(file_two_columns_set)
        total_ids = file_one_id_set.union(file_two_id_set)
        total_ids_array = sorted(total_ids)
        total_ids_array = list(map(int, total_ids_array))
        total_ids_array.sort()
        total_ids_array = list(map(str, total_ids_array))
        columns_intersection = file_one_columns_set.intersection(file_two_columns_set)

        out_file.write(" Input File ,"+"   "   + primary_index_one +   "   ,    Differences (COLUMN_NAME)    ")

        for col in total_columns:
            out_file.write("," + col)

        out_file.write("\n")
        for temp_id in total_ids_array:
            if file_one_id_set.__contains__(temp_id) and file_two_id_set.__contains__(temp_id):
                for temp_column in columns_intersection:
                    if file_one_dictionary.get(temp_id).get(temp_column) != file_two_dictionary.get(temp_id).get(temp_column):
                        out_file.write(" INPUT-1 ," +temp_id + ",")
                        out_file.write(file_one_dictionary.get(temp_id).get(temp_column) + " (" + temp_column + ")")
                        for col in total_columns:
                            if file_one_columns_set.__contains__(col):
                                out_file.write("," + file_one_dictionary.get(temp_id).get(col))
                            else:
                                out_file.write(", COLUMN NOT PRESENT ")
                        out_file.write("\n INPUT-2 ," + temp_id + ",")
                        out_file.write(file_two_dictionary.get(temp_id).get(temp_column) + " (" + temp_column + ")")
                        for col in total_columns:
                            if file_two_columns_set.__contains__(col):
                                out_file.write("," + file_two_dictionary.get(temp_id).get(col))
                            else:
                                out_file.write(", COLUMN NOT PRESENT ")
                        out_file.write("\n")
                out_file.write("\n")
            elif file_one_id_set.__contains__(temp_id) and (not file_two_id_set.__contains__(temp_id)):
                out_file.write(" INPUT-1 ,"+temp_id + ",")
                out_file.write(" ENTRY PRESENT ")
                for col in total_columns:
                    if file_one_columns_set.__contains__(col):
                        out_file.write("," + file_one_dictionary.get(temp_id).get(col))
                    else:
                        out_file.write(", COLUMN NOT PRESENT ")
                out_file.write("\n INPUT-2 ," + temp_id + ",")
                out_file.write(" ENTRY NOT PRESENT")
                for col in total_columns:
                    if file_two_columns_set.__contains__(col):
                        out_file.write(", ENTRY NOT PRESENT")
                    else:
                        out_file.write(", COLUMN NOT PRESENT ")
                out_file.write("\n\n")
            elif (not file_one_id_set.__contains__(temp_id)) and file_two_id_set.__contains__(temp_id):
                out_file.write(" INPUT-1 ,"+temp_id + ",")
                out_file.write(" ENTRY NOT PRESENT ")
                for col in total_columns:
                    if file_one_columns_set.__contains__(col):
                        out_file.write(", ENTRY NOT PRESENT")
                    else:
                        out_file.write(", COLUMN NOT PRESENT ")
                out_file.write("\n INPUT-2 ," + temp_id + ",")
                out_file.write(" ENTRY PRESENT")
                for col in total_columns:
                    if file_two_columns_set.__contains__(col):
                        out_file.write("," + file_two_dictionary.get(temp_id).get(col))
                    else:
                        out_file.write(", COLUMN NOT PRESENT ")
                out_file.write("\n\n")

        if len(filenames) == 2:
            flash('Files compared successfully.\n The \'result\' & \'entries-not-present\' files are stored at \"' +
                  app.config['FILES_FOLDER'] + '\"')
            session['filenames'] = None

    else:
        flash('Please upload the files first')
        session['filenames'] = None

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
