# -*- coding: utf-8 -*-

# Import other stuff here

import pytest
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
