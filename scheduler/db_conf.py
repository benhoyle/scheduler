# -*- coding: utf-8 -*-

# Create DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


# Define name and path for SQLite3 DB
db_name = "data.db"
db_path = os.path.join(os.getcwd(), db_name)
engine = create_engine('sqlite:///' + db_path, echo=False)

# Setup SQLAlchemy session
Session = sessionmaker(bind=engine)


class SessionManager(object):
    def __init__(self):
        self.session = Session()
