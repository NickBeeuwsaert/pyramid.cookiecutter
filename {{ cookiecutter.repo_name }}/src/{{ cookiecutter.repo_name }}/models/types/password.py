from sqlalchemy import Text, event
from sqlalchemy.orm import mapper
from sqlalchemy.types import TypeDecorator

from passlib.context import LazyCryptContext


class Password:
    def __init__(self, hash, context):
        self.hash = hash
        self.context = context

    def __eq__(self, rhs):
        return self.context.verify(rhs, self.hash)


class PasswordType(TypeDecorator):
    impl = Text

    def __init__(self, **kwargs):
        super().__init__()
        self.context = LazyCryptContext(**kwargs)

    def process_bind_param(self, value, dialect):
        return self.coerce(value).hash

    def process_result_value(self, value, dialect):
        return Password(value, self.context)

    def coerce(self, value):
        if isinstance(value, Password):
            return value

        return Password(self.context.hash(value), self.context)


@event.listens_for(mapper, "mapper_configured")
def mapper_configured(mapper, cls):
    if mapper.non_primary:
        return

    for prop in mapper.column_attrs:
        column = getattr(cls, prop.key)
        if not isinstance(column.type, PasswordType):
            continue

        def set(target, value, oldvalue, initiator):
            return column.type.coerce(value)

        event.listen(column, "set", set, retval=True)
