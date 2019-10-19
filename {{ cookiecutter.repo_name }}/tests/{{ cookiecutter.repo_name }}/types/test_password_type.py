import pytest
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from {{ cookiecutter.repo_name }}.models.types.password import Password, PasswordType


@pytest.fixture
def connection():
    return sa.create_engine("sqlite:///:memory:", echo=True)

@pytest.fixture
def Base():
    return declarative_base()

@pytest.fixture
def session(Base, connection):
    Base.metadata.create_all(bind=connection)
    Session = sa.orm.sessionmaker(bind=connection)
    return Session()

@pytest.fixture
def User(Base):
    class User(Base):
        __tablename__ = 'users'

        id = sa.Column(sa.Integer, primary_key=True)
        username = sa.Column(sa.Text, unique=True)
        password = sa.Column(PasswordType(
            schemes=['md5_crypt']
        ))
    return User

def test_setting_password_hashes_password_automatically(session, User):
    user = User(username="some_user", password="some_password")
    assert isinstance(user.password, Password), "Setting password should automatically hash password"

def test_rehashes_passwords(User):
    user = User(username='a', password='b')
    initial_password = user.password
    user.password = 'asdf'

    assert user.password is not initial_password
