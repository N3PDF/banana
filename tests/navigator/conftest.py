# -*- coding: utf-8 -*-
import pytest
import sqlalchemy.orm

from banana.data import db


@pytest.fixture
def dbsession(banana_yaml):
    "Setup banana database"
    db_path = banana_yaml["paths"]["database"]
    engine = db.engine(db_path)
    db.create_db(db.Base, engine)
    db.Base.metadata.bind = engine
    session = sqlalchemy.orm.sessionmaker(bind=engine)()
    yield session
    session.close()
    db_path.unlink()
