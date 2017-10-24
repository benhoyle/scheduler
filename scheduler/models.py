# -*- coding: utf-8 -*-

# Skeleton for setting up a basic SQLAlchemy mapping to a SQLite 3 DB
import os
from datetime import datetime

from dateutil import parser

# Create DB
from sqlalchemy import create_engine

# Setup imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

# Define Class for Excluded Matter Case Details
from sqlalchemy import Column, Integer, String, Boolean, Text, \
                        ForeignKey, DateTime

# Define name and path for SQLite3 DB
db_name = "data.db"
db_path = os.path.join(os.getcwd(), db_name)
engine = create_engine('sqlite:///' + db_path, echo=False)

# Setup SQLAlchemy session
Session = sessionmaker(bind=engine)
session = Session()

class Base(object):
    """ Extensions to Base class. """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

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

    def save(self):
        """
        Save a model instance.

        :return: Model instance
        """
        session.add(self)
        session.commit()

        return self

    def delete(self):
        """
        Delete a model instance.

        :return: session.commit()'s result
        """
        session.delete(self)
        return session.commit()

Base = declarative_base(cls=Base)


# Task Models
class Task(Base):
    """Object representing a task to be completed."""

    taskref = Column(String(128))
    tasktype = Column(String(256))
    description = Column(Text)
    esttimemins = Column(Integer, default=30)
    due = Column(DateTime(timezone=True))

    critical = Column(Boolean)
    # Amount task is completed as an integer percentage
    # - 100 = complete, 0 = not started
    progress = Column(Integer, default=0)

    timeperiods = relationship("TimePeriod", back_populates="task")

    def __init__(
        self, duedate, time_estimate, taskref=None, tasktype=None,
        description=None, timetype="minutes"
    ):
        """ Initialise object - needs at least a duedate and time est. """

        if not isinstance(duedate, datetime):
            duedate = parser.parse(duedate)
        self.due = duedate

        if timetype == "hours":
            time_estimate = int(time_estimate)*60
        self.esttimemins = time_estimate

        self.taskref = taskref
        self.tasktype = tasktype
        self.description = description

    @property
    def assigned(self):
        """ Has task been assigned to time periods."""
        # If sum of duration for timeperiods ~ esttimemins = True
        pass

    @property
    def duedate(self):
        """ Date component of due datetime."""
        pass

    @property
    def duetime(self):
        """ Time component of due datetime."""
        pass

    def reset_assignments(self):
        """ Clear all existing assignments. """
        for timeperiod in self.timeperiods:
            self.timeperiods.remove(timeperiod)


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
        return not self.task

    @property
    def duration(self):
        """ Duration of time period in minutes. """
        pass
    # To schedule we split a time period into two - one with assigned time
    # one as available period left over

# Create new DB
Base.metadata.create_all(engine)

