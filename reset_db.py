from app import app,db
from models import File


with app.app_context():
    
    db.create_all()
    print('DATABASE CREATED SUCCESSFULLY')

    inspector = db.inspect(db.engine)
    print("Tables:", inspector.get_table_names())