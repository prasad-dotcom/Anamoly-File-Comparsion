import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
#from flask import render_template
#imports for backend logic
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter


from werkzeug.utils import secure_filename
from flask_admin import Admin
from extensions import db
from app import db
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
#from LOGIC.logic import compare_files








#initialise flask app from config
app = Flask(__name__)
app.config.from_object(Config)

#upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(),'static', 'UPLOAD_FOLDER')
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)




#initialize SQLALchemy

db = SQLAlchemy(app)
migrate = Migrate(app,db)

#Ensuring database existence
with app.app_context():
    db.create_all()

from models import File



#Ensuring the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])








# Constants
PREDEFINED_FILE = 'static/predefined_file/config_master.xlsx'
upload_file = 'static/UPLOAD_FOLDER'



#Check if the file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

#Landing Page
@app.route('/')
def index():
    files = File.query.order_by(File.uploaded_at.desc()).all()
    return render_template("index.html",file=files)

#Renders first_page.html
@app.route('/first_page')
def first_page():
    return render_template("first_page.html",)

#Handles File Upload
@app.route('/upload_file', methods=['POST'])
def upload_file():
    
    if 'file' not in request.files:
        flash('No file part found')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        flash(f'File "{filename}" uploaded successfully')

        # Save the file
        file.save(filepath)

        # Calculate file size
        file_size = os.path.getsize(filepath)

        # Attempt to read Excel content
        try:
            df = pd.read_excel(filepath)
            print(f"File '{filename}' successfully uploaded. First 5 rows:")
            print(df.head())
        except Exception as e:
            flash(f"Error reading Excel file: {e}")
            return redirect(request.url)

        # Save file information to the database
        new_file = File(filename=filename, filepath=filepath, file_size=file_size, uploaded_at=datetime.utcnow())
        db.session.add(new_file)
        db.session.commit()

        flash(f'File "{filename}" uploaded successfully (Size: {file_size / (1024**2):.2f} MB)')
        return redirect(url_for('index'))

    else:
        flash('Invalid file type. Only Excel files (.xlsx, .xls) are allowed.')
        return redirect(url_for('index'))

# route for executing the notebooks
@app.route('/process', methods=['GET'])
def process_file():



    from nbconvert import HTMLExporter
    from nbconvert.preprocessors import ExecutePreprocessor
    import nbformat
    
    
    #from nbformat import read as nb_read
    from nbconvert.preprocessors import ExecutePreprocessor
    """Retrieve latest uploaded file and compare it with predefined file"""
    user_file = File.query.order_by(File.uploaded_at.desc()).first()

    if not user_file:
        return "Please upload a file. Your file is missing."

    user_file_path = user_file.filepath
    predefined_file_path = "../static/predefined_file/config_master.xlsx"
    print("Retrieved user file path:", user_file_path)
    print("Retrieved predefined file path:", predefined_file_path) # Debugging

    #set env variables for script file
    os.environ['USER_FILE_PATH'] = user_file_path
    os.environ['PREDEFINED_FILE_PATH'] = predefined_file_path

    try:
        #import nbformat
        #from nbconvert.preprocessors import ExecutePreprocessor

        # Comparison logic placeholder
        with open ('notebooks/logic_script.ipynb','r',encoding='utf-8') as f:
            nb = nbformat.read(f, as_version= 4)
        
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': './notebooks/'}})

        #Example dummy output to send to HTML page
        #result_table = pd.DataFrame({
        #    "Status": ["Success"],
        #    "Details": ["Comparison completed"]
        #})

        #Export executed notebook to HTML
        html_exporter = HTMLExporter()
        html_exporter.exclude_input = True
        body, _ = html_exporter.from_notebook_node(nb)
    

        return render_template('first_page.html', output_html = body ,index=False)
    #tables=[result_table.to_html(classes='table table-bordered
    #return render_template('first_page.html', output="Comparison results here")  # Replace with actual results
    except Exception as e:
        return f"error executing notebook:{e}"

if __name__ == "__main__":
    app.run(debug=True)
