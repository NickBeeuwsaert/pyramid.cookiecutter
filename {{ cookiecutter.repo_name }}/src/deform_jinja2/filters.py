from jinja2 import Undefined, escape, evalcontextfilter
from markupsafe import Markup


@evalcontextfilter
def do_htmlattr(ctx, mapping, prepend_whitespace=True):
    """This filter is very similar to jinja2's builtin xmlattr
    filter, except it removes False in addition to None and Undefined,
    and renders True using HTML5 empty attribute syntax"""
    attributes = " ".join(
        escape(key) if value is True else f'{escape(key)}="{escape(value)}"'
        for key, value in mapping.items()
        if value is not False and value is not None and not isinstance(value, Undefined)
    )

    if prepend_whitespace is True and attributes:
        attributes = f' {attributes}'
    
    if ctx.autoescape:
        attributes = Markup(attributes)

    return attributes
