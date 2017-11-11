# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scheduler.models import TimePeriod, Task

import pytest

@pytest.yield_fixture(scope='session')
def engine():
    _engine = create_engine('sqlite://')
    yield _engine


@pytest.yield_fixture(scope='session')
def session(engine):
    # Setup SQLAlchemy session
    Session = sessionmaker(bind=engine)
    _session = Session()
    yield _session


@pytest.yield_fixture(scope='function')
def timeperiods(session):
    pass
