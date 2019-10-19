import colander
from sqlalchemy import literal


class FieldTaken(colander.deferred):
    def __init__(self, field, msg):
        self.field = field
        self.msg = msg

    def __call__(self, node, kw):
        request = kw["request"]
        db = request.db

        def validator(node, cstruct):
            if db.query(literal(True)).filter(self.field == cstruct).scalar():
                raise colander.Invalid(node, self.msg)

        return validator
