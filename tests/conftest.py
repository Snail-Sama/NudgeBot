import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bot import create_app
from config import TestConfig
from nudge_bot.db import db
from sqlalchemy.orm import scoped_session, sessionmaker

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session

@pytest.fixture(scope="session")
def app():
    
    from config import TestConfig
    from app import create_app

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def session():
    """Creates a scoped session compatible with Flask-SQLAlchemy 3.x."""
    connection = db.engine.connect()
    transaction = connection.begin()

    session_factory = sessionmaker(bind=connection)
    Session = scoped_session(session_factory)

    db.session = Session  # Override the global scoped session

    yield Session

    transaction.rollback()
    connection.close()
    Session.remove()