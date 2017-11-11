# -*- coding: utf-8 -*-

from scheduler.models import Task, TimePeriod

from scheduler.google_api import (
    get_tasks_from_sheet, get_work_blocks, post_assigned_time,
    clear_events
)

# Import date & time functions
from datetime import timedelta, datetime


def reset_assignments(task):
    pass


def run():
    """ Run program."""
    # Clear initial data
    Task.delete_all()
    TimePeriod.delete_all()
    # Clear output calendar
    clear_events()
    # Get tasks from Google spreadsheet
    tasks = get_tasks_from_sheet()
    # Get working blocks from Input Google calendar
    wb = get_work_blocks()
    # Save data
    for t in tasks:
        t.save()
    for w in wb:
        w.save()
    # Schedule tasks
    errors = schedule_all()
    # Upload scheduled time periods to Output Google calendar
    assigned_tps = TimePeriod.get_assigned()
    events = [a_tp.as_event() for a_tp in assigned_tps]
    posted_events = post_assigned_time(events)
    # Return errors and posted events
    return (errors, posted_events)


def schedule_all():
    """ Schedule all tasks."""
    # Get all unassigned tasks
    tasks = Task.get_all()
    errors = list()
    for task in tasks:
        timeleft = schedule_task(task)
        if timeleft > 0:
            errors.append({'task': task, 'timeleft': timeleft})
    return errors


def schedule_task(task, startdate=datetime.now()):
    """ Schedule a single task. """
    # Initialise variable to store amount of time to assign
    runningtime = task.esttimemins*(1-(task.progress/100.0))

    # Get all available timeperiods with a datetime > startdate
    # And an enddate < duedate
    available_tp = TimePeriod.unassigned_in_range(startdate, task.due)
    while available_tp and runningtime > 0:
        if runningtime >= available_tp.duration:
            # Assign task to time period
            available_tp.task = task
            available_tp.save()
            # Reduce running time
            runningtime = runningtime - available_tp.duration
            available_tp = TimePeriod.unassigned_in_range(startdate, task.due)
        else:
            # time period duration is longer than task duration
            # We need to adjust the statement below to work with timedeltas
            new_enddatetime = (
                available_tp.startdatetime +
                timedelta(seconds=runningtime*60)
            )
            original_enddatetime = available_tp.enddatetime
            # Split time period into two periods
            available_tp.enddatetime = new_enddatetime
            new_tp_2 = TimePeriod(new_enddatetime, original_enddatetime)
            # Assign first time period to task
            available_tp.task = task
            available_tp.save()
            new_tp_2.save()
            # Set next available time period as time period 2
            available_tp = TimePeriod.unassigned_in_range(startdate, task.due)
            runningtime = 0

    return runningtime
