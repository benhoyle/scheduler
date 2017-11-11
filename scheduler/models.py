# -*- coding: utf-8 -*-

# Skeleton for setting up a basic SQLAlchemy mapping to a SQLite 3 DB
from datetime import datetime
from dateutil import parser
import pytz

from math import ceil, floor

import json

# Setup imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

# Define Class for Excluded Matter Case Details
from sqlalchemy import Column, Integer, String, Boolean, Text, \
                        ForeignKey, DateTime

from scheduler.db_conf import session

Base = declarative_base()


class ExtMixin(object):
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

    def __repr__(self):
        return json.dumps(self.as_dict())

    @classmethod
    def get_all(cls):
        """ Get all objects."""
        return session.query(cls).all()

    @classmethod
    def delete_all(cls):
        """ Delete all objects."""
        session.query(cls).delete()
        return session.commit()


# Task Models
class Task(ExtMixin, Base):
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
        time_left = floor(
            self.esttimemins*(1-(self.progress/100.0))
        )
        tp_times = sum([tp.duration for tp in self.timeperiods])
        return tp_times >= time_left

    def reset_assignments(self):
        """ Clear all existing assignments. """
        for timeperiod in self.timeperiods:
            self.timeperiods.remove(timeperiod)


class TimePeriod(ExtMixin, Base):
    """Object representing a block of time in a calendar."""

    startdatetime = Column(DateTime(timezone=True))
    enddatetime = Column(DateTime(timezone=True))
    description = Column(String(128))
    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", back_populates="timeperiods")

    def __init__(self, start, end):
        if start.tzinfo:
            self.startdatetime = start.astimezone(pytz.utc)
        else:
            self.startdatetime = start
        if end.tzinfo:
            self.enddatetime = end.astimezone(pytz.utc)
        else:
            self.enddatetime = end

    @property
    def available(self):
        """ Is time period available for assignment."""
        return not self.task

    @property
    def duration(self):
        """ Duration of time period in minutes. """
        return ceil(
            (self.enddatetime - self.startdatetime).total_seconds() / 60.0
            )

    @classmethod
    def unassigned_in_range(cls, startdate, enddate):
        """ Get first unassigned time period in the supplied
        date range. Ordered by startdatetime.

        """
        return session.query(cls).filter(cls.task_id == None) \
            .filter(cls.startdatetime >= startdate) \
            .filter(cls.enddatetime <= enddate) \
            .order_by(cls.startdatetime).first()

    @classmethod
    def get_assigned(cls):
        """ Get all assigned time periods."""
        return session.query(cls).filter(cls.task_id != None).all()

    def as_event(self):
        """ Output the time period in a dict format that can be
        easily added as an event to Google calendar."""
        if self.task:
            summary = self.task.taskref
            desc = self.task.description
        else:
            summary = None
            desc = self.description

        return {
            'summary': summary,
            'description': desc,
            'start': {
                'dateTime': self.startdatetime.isoformat(),
                'timeZone': pytz.utc.zone
            },
            'end': {
                'dateTime': self.enddatetime.isoformat(),
                'timeZone': pytz.utc.zone
            }
        }
