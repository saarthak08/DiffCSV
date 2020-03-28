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

        fileone = t1.readlines()

        filetwo = t2.readlines()

        t1.close()

        t2.close()

        outFile = open('result.' + filenames[0].rsplit('.', 1)[1].lower(), 'w')
        notPresentFile2 = open("entries-not-present-in-input-1-but-present-in-input-2."+filenames[0].rsplit('.', 1)[1].lower(), 'w')
        notPresentFile1 = open("entries-not-present-in-input-2-but-present-in-input-1."+filenames[0].rsplit('.', 1)[1].lower(), 'w')

        file_one_array = []
        file_two_array = []
        columns = []

        with open(filenames[0]) as csvone:
            csvreader_one = csv.reader(csvone)
            for row in csvreader_one:
                file_one_array.append(row)

        with open(filenames[1]) as csvtwo:
            csvreader_two = csv.reader(csvtwo)
            for row in csvreader_two:
                file_two_array.append(row)

        outFile.write("   "+file_one_array[0][0] + "   ,    Differences (COLUMN_NAME)    ")
        notPresentFile2.write("   "+file_one_array[0][0] + "   ,    Differences (COLUMN_NAME)    ")
        notPresentFile1.write("   "+file_one_array[0][0] + "   ,    Differences (COLUMN_NAME)    ")


        for col_one in file_one_array[0][1:]:
            for col_two in file_two_array[0][1:]:
                if col_one == col_two:
                    columns.append(col_one)
                    outFile.write(","+col_one)
                    notPresentFile2.write(","+col_one)
                    notPresentFile1.write(","+col_one)

        outFile.write("\n")
        notPresentFile2.write("\n")
        notPresentFile1.write("\n")


        matched_column = None
        flag = False
        flag2 = False

        for i in range(1, len(file_one_array)):
            flag = False
            for j in range(1, len(file_two_array)):
                if file_one_array[i][0] == file_two_array[j][0]:
                    flag = True
                    for x in range(len(file_one_array[0])):
                        for y in range(len(file_two_array[0])):
                            if file_one_array[0][x] == file_two_array[0][y]:
                                matched_column = file_one_array[0][x]
                                break
                            else:
                                matched_column = None
                        if matched_column is not None:
                            if file_one_array[i][x] != file_two_array[j][y]:
                                outFile.write(file_one_array[i][0]+",")
                                outFile.write(file_one_array[i][x]+" ("+matched_column+")")
                                for col in range(1, len(file_one_array[0])):
                                    for col2 in range(len(columns)):
                                        if file_one_array[0][col] == columns[col2]:
                                            outFile.write(","+file_one_array[i][col])
                                outFile.write("\n"+file_two_array[j][0]+",")
                                outFile.write(file_two_array[j][y]+" ("+matched_column+")")
                                for col in range(len(file_two_array[0])):
                                    for col2 in range(len(columns)):
                                        if file_two_array[0][col] == columns[col2]:
                                            outFile.write(","+file_two_array[j][col])
                                outFile.write("\n")
                    outFile.write("\n")
            if not flag:
                notPresentFile1.write(file_one_array[i][0] + ",")
                notPresentFile1.write(" PRESENT ")
                for col in range(1, len(file_one_array[0])):
                    for col2 in range(len(columns)):
                        if file_one_array[0][col] == columns[col2]:
                            notPresentFile1.write("," + file_one_array[i][col])
                notPresentFile1.write("\n" + file_one_array[i][0] + ",")
                notPresentFile1.write(" NOT PRESENT ")
                for col in range(len(file_two_array[0])):
                    for col2 in range(len(columns)):
                        if file_two_array[0][col] == columns[col2]:
                            notPresentFile1.write(", NOT PRESENT ")
                notPresentFile1.write("\n\n")


        for p in range(1, len(file_two_array)):
            flag2 = False
            for q in range(1, len(file_one_array)):
                if file_two_array[p][0] == file_one_array[q][0]:
                    flag2 = True
            if not flag2:
                notPresentFile2.write(file_two_array[p][0] + ",")
                notPresentFile2.write(" NOT PRESENT ")
                for col in range(1, len(file_one_array[0])):
                    for col2 in range(len(columns)):
                        if file_one_array[0][col] == columns[col2]:
                            notPresentFile2.write("," + " NOT PRESENT")
                notPresentFile2.write("\n" + file_two_array[p][0] + ",")
                notPresentFile2.write(" PRESENT ")
                for col in range(len(file_two_array[0])):
                    for col2 in range(len(columns)):
                        if file_two_array[0][col] == columns[col2]:
                            notPresentFile2.write("," + file_two_array[p][col])
                notPresentFile2.write("\n\n")


        """
        for i in range(0, len(file_one_array)):
            if file_one_array[i] != file_two_array[x]:
                y = 0
                for col in file_one_array[i]:
                    if col != file_two_array[x][y]:
                        outFile.write(str(x) + ",")
                        outFile.write(col + " (" + file_one_array[0][y] + "),")
                        outFile.write(fileone[x])
                        outFile.write(str(x) + ",")
                        outFile.write(file_two_array[x][y] + " (" + file_one_array[0][y] + "),")
                        outFile.write(filetwo[x] + "\n")
                    y += 1
            x += 1
        """

        if len(filenames) == 2:
            flash('Files compared successfully.\n The \'result\' & \'entries-not-present\' files are stored at \"' + app.config['FILES_FOLDER']+'\"')
            session['filenames'] = None

    else:
        flash('Please upload the files first')
        session['filenames'] = None

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
