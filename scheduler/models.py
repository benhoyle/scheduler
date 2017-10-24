# -*- coding: utf-8 -*-

# Skeleton for setting up a basic SQLAlchemy mapping to a SQLite 3 DB
import os
from datetime import datetime

# Define name and path for SQLite3 DB
db_name = "data.db"
db_path = os.path.join(os.getcwd(), db_name)

# Create DB
from sqlalchemy import create_engine
engine = create_engine('sqlite:///' + db_path, echo=False)

# Setup imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

# Define Class for Excluded Matter Case Details
from sqlalchemy import Column, Integer, String, Date, Boolean, Text, \
                        ForeignKey, DateTime

class Base(object):
    """ Extensions to Base class. """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)

    def as_dict(self):
        """ Return object as a dictionary. """
        temp_dict = {}
        temp_dict['object_type'] = self.__class__.__name__
        for c in self.__table__.columns:
            cur_attr = getattr(self, c.name)
            # If datetime generate string representation
            if isinstance(cur_attr, datetime):
                cur_attr = cur_attr.strftime('%d %B %Y - %H %M')
            temp_dict[c.name] = cur_attr
        return temp_dict

Base = declarative_base(cls=Base)

class ParentModel(Base):
    """ Model for a parent entity. """
    # Example name field
    name = Column(String(256))

    # Relationship for children
    children = relationship("ChildModel", backref="parent")

class ChildModel(Base):
    """ Model for a child entity. """
    # Example name field
    name = Column(String(256))

    # Foreign key for parent
    parent_id = Column(Integer, ForeignKey('parentmodel.id'))

# Task Models
class Task(Base):
    """Object representing a task to be completed."""

    taskref = Column(String(128))
    tasktype = Column(String(256))
    description = Column(Text)
    esttimemins = Column(Integer, default=30)
    due = Column(DateTime(timezone=True))

    critical = Column(Boolean)
    #Amount task is completed as an integer percentage - 100 = complete, 0 = not started
    progress = Column(Integer, default=0)

    timeperiods = relationship("TimePeriod", back_populates="task")

    @property
    def assigned(self):
        """ Has task been assigned to time periods."""
        pass

    @property
    def duedate(self):
        """ Date component of due datetime."""
        pass

    @property
    def duetime(self):
        """ Time component of due datetime."""
        pass

class TimePeriod(Base):
    """Object representing a block of time in a calendar."""

    startdatetime = Column(DateTime(timezone=True))
    enddatetime = Column(DateTime(timezone=True))
    description = Column(String(128))
    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", back_populates="timeperiods")

    def __init__(self, start, end):
        self.startdatetime = start
        self.enddatetime = end

    @property
    def available(self):
        """ Is time period available for assignment."""
        return not task

    @property
    def duration(self):
        """ Duration of time period in minutes. """
        pass
    # To schedule we split a time period into two - one with assigned time
    # one as available period left over



# Create new DB
Base.metadata.create_all(engine)

# Setup SQLAlchemy session
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
