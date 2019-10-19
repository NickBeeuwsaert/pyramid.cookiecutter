from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.view import view_config


@view_config(
    route_name='index',
    renderer='index.jinja2'
)
def index(request: Request):
    request.session['counter'] = request.session.get('counter', 0) + 1
    return {
        'counter': request.session['counter']
    }

def includeme(config: Configurator):
    config.scan(__name__)
    config.include('.users', route_prefix='/users')
    config.add_route('index', '/')
