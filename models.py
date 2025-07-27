from app import db
from datetime import datetime,timezone




class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    


    def __init__(self, filename, filepath, file_size,uploaded_at = None):
        self.filename = filename
        self.filepath = filepath
        self.file_size = file_size
        if uploaded_at:
            self.uploaded_at = uploaded_at





    def __repr__(self):
        return f"<File {self.filename}:{self.id} : {self.filepath}: {self.file_size}: {self.uploaded_at}>"

