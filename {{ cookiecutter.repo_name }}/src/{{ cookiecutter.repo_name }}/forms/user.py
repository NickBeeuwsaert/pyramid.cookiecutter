import colander
from deform.widget import PasswordWidget

from {{ cookiecutter.repo_name }}.models.user import User

from . import CSRFSchema
from .validators import FieldTaken


class CreateUserSchema(CSRFSchema):
    name = colander.SchemaNode(
        colander.String(),
        validator=FieldTaken(User.name, "That username is already taken!")
    )
    password = colander.SchemaNode(colander.String(), widget=PasswordWidget())

class LoginSchema(CSRFSchema):
    name = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String(), widget=PasswordWidget())


    @colander.deferred
    def request(node, kw):
        return kw["request"]


    def deserialize(self, cstruct):
        db = self.request.db
        cstruct = super().deserialize(cstruct)

        user = db.query(User).filter(User.name == cstruct['name']).first()
        if user and user.password == cstruct['password']:
            return user

        raise colander.Invalid(self, "Invalid username or password!")
