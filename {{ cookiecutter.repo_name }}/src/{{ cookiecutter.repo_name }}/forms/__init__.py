import colander
from deform.widget import HiddenWidget
from pyramid.csrf import check_csrf_token, get_csrf_token


class CSRFSchema(colander.MappingSchema):
    @colander.instantiate()
    class csrf_token(colander.SchemaNode):
        schema_type = colander.String
        widget = HiddenWidget()

        @colander.deferred
        def default(node, kw):
            request = kw["request"]

            return get_csrf_token(request)

        @colander.deferred
        def validator(node, kw):
            request = kw["request"]

            def validator(node, cstruct):
                # check_csrf_token will also check the X-CSRF-Token
                # request header. Also, not sure if I should even do
                # validation here since pyramid can automatically
                # do CSRF validation on unsafe HTTP methods
                if not check_csrf_token(request, node.name, raises=False):
                    raise colander.Invalid(node, "Invalid CSRF Token!")

            return validator
