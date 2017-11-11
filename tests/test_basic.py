# -*- coding: utf-8 -*-

# Import other stuff here

from datetime import datetime

from scheduler.models import (
    Task, TimePeriod
)


class TestGeneral:
    """Basic test cases."""

    def test_creation(self):
        """ Test generating objects of each type."""
        test_task = Task(datetime.now(), 6)
        test_timeperiod = TimePeriod(datetime.now(), datetime.now())

        assert test_task.as_dict()['object_type'] == 'Task'
        assert test_timeperiod.as_dict()['object_type'] == 'TimePeriod'

    def test_duration(self):
        """ Test getting duration of a time period."""
        test_timeperiod = TimePeriod(
            datetime(2010, 10, 10, 12, 00),
            datetime(2010, 10, 10, 12, 30)
            )
        assert test_timeperiod.duration == 30

    def test_timeperiods(self, timeperiods):
        """ Test time periods."""
        tps = TimePeriod.get_all()
        assert len(tps) == 2
        assert "10 October 2010 - 12 30" in tps[0].__repr__()
        assert tps[1].available
        startdate = datetime(2010, 10, 10, 11, 00)
        enddate = datetime(2010, 12, 10, 12, 00)
        unassigned = TimePeriod.unassigned_in_range(startdate, enddate)
        assert "10 October 2010 - 12 30" in unassigned.__repr__()
        assert "2010-10-10" in unassigned.as_event()['start']['dateTime']

    def test_tasks(self, tasks):
        """ Test task functions."""
        tasks = Task.get_all()
        assert len(tasks) == 2
        tasks[0].delete()
        tasks = Task.get_all()
        assert len(tasks) == 1
        assert not tasks[0].assigned

    def test_assignments(self, tasks, timeperiods):
        """ Check manual assignments."""
        tps = TimePeriod.get_all()
        tasks = Task.get_all()
        assert tps[0].available and tps[1].available
        tps[0].task = tasks[0]
        tps[1].task = tasks[1]
        tps[0].save()
        tps[1].save()
        assert not tps[0].available and not tps[1].available
        assert len(TimePeriod.get_assigned()) == 2
        assert "test1" in tps[0].as_event()['description']
        tasks[0].reset_assignments()
        assert tps[0].available and not tps[1].available
