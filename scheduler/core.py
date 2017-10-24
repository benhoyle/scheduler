# -*- coding: utf-8 -*-

from scheduler.models import Task, TimePeriod

# Import date & time functions
from datetime import time, timedelta, datetime




def reset_assignments(task):


def schedule_all():
    """ Schedule all tasks."""
    # Get all unassigned tasks
    for task in tasks:
        schedule_task(task)
    pass

def schedule_task(task, startdate=None):
    """ Schedule a single task. """
    pass
    # Get all available timeperiods with a datetime > startdate
