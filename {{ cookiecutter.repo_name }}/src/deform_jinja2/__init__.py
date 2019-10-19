"""
Custom jinja2 form controls for deform
"""
from deform import Form as BaseForm
from jinja2 import Environment, PackageLoader
from markupsafe import Markup

from .filters import do_htmlattr


class Jinja2RendererFactory:
    def __init__(self, loader):
        environment = Environment(
            loader=loader,
            autoescape=True
        )
        environment.filters['htmlattr'] = do_htmlattr
        self.environment = environment


    def __call__(self, template_name, **kw):
        template = self.environment.get_template(f'{template_name}.jinja2')
        return Markup(template.render(**kw))

default_loader = PackageLoader('deform_jinja2', 'templates')

class Form(BaseForm):
    default_renderer = Jinja2RendererFactory(default_loader)
