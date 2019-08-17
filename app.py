from flask import Flask

 

UPLOAD_FOLDER = '/Users/saarthak08/Downloads/'

 

app = Flask(__name__)

app.debug=True

app.secret_key = "secret key"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024