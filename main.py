import os

from app import app

from flask import Flask, flash, request, redirect, render_template, session, send_file

from werkzeug.utils import secure_filename

import csv

ALLOWED_EXTENSIONS = set(['csv'])

filenames = []


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def compare_filenames(files):
    return files[0].rsplit('.', 1)[1].lower() == files[1].rsplit('.', 1)[1].lower()


@app.route('/download', methods=['POST', 'GET'])
def download_file():
    try:
        return send_file(app.config['UPLOAD_FOLDER'] + '/result.csv', attachment_filename='result.csv',
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

    if request.method == 'POST':

        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        if files is not None:

            for file in files:

                if file.filename == '':
                    flash('No file selected for uploading.')
                    filenames = []
                    return redirect(request.url)

                if not (file and allowed_file(file.filename)):
                    filenames = []
                    flash('Allowed file type is csv only.')
                    return redirect(request.url)

                filename = secure_filename(file.filename)

                filenames.append(file.filename)

            if len(filenames) == 2 and compare_filenames(filenames):
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
        outFile.write(" S.No. ,    Differences (COLUMN_NAME)    ,")

        for row in fileone[:1]:
            for col in row:
                outFile.write(col),

        x = 0
        rows_one = []
        rows_two = []
        with open(filenames[0]) as csvone:
            csvreader_one = csv.reader(csvone)
            for row in csvreader_one:
                rows_one.append(row)

        with open(filenames[1]) as csvtwo:
            csvreader_two = csv.reader(csvtwo)
            for row in csvreader_two:
                rows_two.append(row)

        for i in range(0, len(rows_one)):
            if (rows_one[i] != rows_two[x]):
                y = 0
                for col in rows_one[i]:
                    if col != rows_two[x][y]:
                        outFile.write(str(x) + ",")
                        outFile.write(col + " (" + rows_one[0][y] + "),")
                        outFile.write(fileone[x])
                        outFile.write(str(x) + ",")
                        outFile.write(rows_two[x][y] + " (" + rows_one[0][y] + "),")
                        outFile.write(filetwo[x] + "\n")
                    y += 1
            x += 1

        if len(filenames) == 2:
            flash('Files Compared Successfully')
            session['filenames'] = None

    else:
        flash('Please upload the files first')
        session['filenames'] = None

    return redirect('/')


if __name__ == "__main__":
    app.run()
