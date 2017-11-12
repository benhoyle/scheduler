# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scheduler.models import TimePeriod, Task, Base

import pytest
import pytz

from datetime import datetime


@pytest.yield_fixture(scope='module')
def session():
    _engine = create_engine('sqlite://')
    Base.metadata.create_all(_engine)
    _Session = sessionmaker(bind=_engine)
    _session = _Session()
    yield _session


@pytest.fixture(scope='function')
def timeperiods(session):
    TimePeriod.delete_all()
    TimePeriod(
            datetime(2010, 10, 10, 12, 00),
            datetime(2010, 10, 10, 12, 30)
            ).save()
    tz = pytz.timezone("US/Pacific")
    aware1 = tz.localize(datetime(2010, 10, 11, 12, 00))
    aware2 = tz.localize(datetime(2010, 10, 11, 12, 30))
    TimePeriod(
            aware1,
            aware2
            ).save()
    return session


@pytest.fixture(scope='function')
def tasks(session):
    Task.delete_all()
    Task(
            datetime(2010, 10, 20, 12, 00),
            30,
            description = "test1"
            ).save()
    Task(
            "20 October 2010",
            1, timetype="hours",
            description = "test2"
            ).save()
    return session
