import os
import shutil

from main import main_api

from flask import Flask

cwd = os.getcwd()

FILES_FOLDER = os.path.join(cwd, 'files')

if os.path.exists(FILES_FOLDER):
    shutil.rmtree(FILES_FOLDER)
    os.mkdir(FILES_FOLDER)
else:
    os.mkdir(FILES_FOLDER)

app = Flask(__name__)

app.secret_key = "secret key"

app.config['FILES_FOLDER'] = FILES_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

app.register_blueprint(main_api)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
