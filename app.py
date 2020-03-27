from flask import Flask
import os

cwd = os.getcwd()

FILES_FOLDER = os.path.join(cwd,'files')

if not os.path.exists(FILES_FOLDER):
    os.mkdir(FILES_FOLDER)

app = Flask(__name__)

app.secret_key = "secret key"

app.config['FILES_FOLDER'] = FILES_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
