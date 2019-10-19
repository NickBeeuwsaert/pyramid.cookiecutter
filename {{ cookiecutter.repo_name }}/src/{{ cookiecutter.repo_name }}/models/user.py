import sqlalchemy as sa
from sqlalchemy.orm import relationship

from . import Base
from .types import PasswordType


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True)
    password = sa.Column(PasswordType(schemes=["sha256_crypt"]))
