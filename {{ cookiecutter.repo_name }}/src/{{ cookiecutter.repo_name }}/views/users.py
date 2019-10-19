from deform import Button, ValidationFailure
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget, remember
from pyramid.view import view_config, view_defaults

from deform_jinja2 import Form
from {{ cookiecutter.repo_name }}.forms.user import CreateUserSchema, LoginSchema
from {{ cookiecutter.repo_name }}.models.user import User


@view_defaults(route_name="user.register", renderer="user/register.jinja2")
class RegisterView:
    def __init__(self, request):
        self.request = request

    @reify
    def form(self):
        return Form(
            CreateUserSchema().bind(request=self.request),
            buttons=[
                Button("reset", "Reset", type="reset"),
                Button("register", "Register"),
            ],
        )

    @view_config(request_method=("GET",))
    def get(self):
        return dict(form=self.form)

    @view_config(request_method=("POST",))
    def post(self):
        try:
            data = self.form.validate(self.request.POST.items())
        except ValidationFailure:
            return dict(form=self.form)

        self.request.db.add(User(name=data["name"], password=data["password"]))
        self.request.db.flush()

        return HTTPFound(self.request.route_url("user.login"))

@view_defaults(route_name="user.login", renderer="user/login.jinja2")
class LoginView:
    def __init__(self, request):
        self.request = request

    @reify
    def form(self):
        return Form(
            LoginSchema().bind(request=self.request),
            buttons=('Login',)
        )

    @view_config(request_method=("GET",))
    def get(self):
        return dict(form=self.form)

    @view_config(request_method=("POST",))
    def post(self):
        try:
            user = self.form.validate(self.request.POST.items())
        except ValidationFailure:
            return dict(form=self.form)

        return HTTPFound(self.request.route_url("index"), headers=remember(self.request, user.id))


@view_config(route_name="user.logout")
def logout(request):
    return HTTPFound(request.route_url("index"), headers=forget(request))

def includeme(config):
    config.add_route("user.register", "/register")
    config.add_route("user.login", "/login")
    config.add_route("user.logout", "/logout")
