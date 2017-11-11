# -*- coding: utf-8 -*-

from datetime import datetime

from scheduler.core import schedule_task
from scheduler.models import Task, TimePeriod

class TestCore:

    def test_schedule_tasks(self, tasks, timeperiods):
        """ Test scheduling a task."""
        tps = TimePeriod.get_all()
        tasks = Task.get_all()
        assert tps[0] not in tasks[0].timeperiods
        rt = schedule_task(tasks[0], datetime(2010, 10, 9, 12, 00))
        assert rt == 0
        assert tps[0] in tasks[0].timeperiods
