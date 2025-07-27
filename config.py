import os

#defining the base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))



class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "instance", "flask.sqlite")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'UPLOAD_FOLDER')
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB limit
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}








