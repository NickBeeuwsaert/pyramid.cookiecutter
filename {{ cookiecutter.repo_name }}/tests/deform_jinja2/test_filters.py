{% raw %}
import pytest
from deform_jinja2.filters import do_htmlattr
from jinja2 import Environment


@pytest.fixture
def environment():
    environment = Environment(autoescape=True)
    environment.filters['htmlattr'] = do_htmlattr

    return environment

def test_falsey_values_get_removed(environment: Environment):
    attributes = environment.from_string('''{{ {
        "false_attribute": false,
        "none_attribute": none,
        "undefined_attribute": undefined,
    }|htmlattr(prepend_whitespace=False) }}''').render()

    assert attributes == "", "Falsey values were not removed from the attribute map"

def test_true_uses_empty_attribute_syntax(environment: Environment):
    attributes = environment.from_string('''{{ {
        'empty_attribute': True
    }|htmlattr(prepend_whitespace=False) }}''').render()

    assert attributes == 'empty_attribute', "True value was not rendered as an empty attribute"

def test_attributes_are_rendered_with_values(environment: Environment):
    attributes = environment.from_string('''{{ {
        "attribute": 123,
        "some_attribute": 0,
        "second_attribute": [],
        "another_attribute": "0",
    }|htmlattr(prepend_whitespace=False) }}''').render().split(' ')

    assert 'attribute="123"' in attributes
    assert 'some_attribute="0"' in attributes
    assert 'second_attribute="[]"' in attributes
    assert 'another_attribute="0"' in attributes

@pytest.mark.parametrize(
    'attributes,expected',
    [
        (
            {"malicious_attribute": '" onload="alert("hi!") style="'},
            'malicious_attribute="&#34; onload=&#34;alert(&#34;hi!&#34;) style=&#34;"'
        ),
        (
            {"malicious_attribute": '"><h1>Hi!</h1>'},
            'malicious_attribute="&#34;&gt;&lt;h1&gt;Hi!&lt;/h1&gt;"'
        )
    ]
)
def test_autoescape_works(environment: Environment, attributes: str, expected: str):
    rendered_attributes = environment.from_string('''{{
        attributes|htmlattr(prepend_whitespace=False)|e
    }}''').render(attributes=attributes)
    assert rendered_attributes == expected

def test_does_not_escape_when_autoescape_is_disabled(environment: Environment):
    rendered_attributes = environment.overlay(autoescape=False).from_string('''{{
        attributes|htmlattr(prepend_whitespace=False)|e
    }}''').render(attributes={'attr': '&'})
    assert rendered_attributes == 'attr=&#34;&amp;amp;&#34;'

@pytest.mark.parametrize(
    'prepend_space,attributes,expected',
    [
        (True, {}, ''),
        (True, {"attr": 1}, ' attr="1"'),
        (False, {"attr": 1}, 'attr="1"')
    ]
)
def test_prepend_space_works(environment: Environment, prepend_space, attributes, expected):
    rendered_attributes = environment.from_string('''{{
        attributes|htmlattr(prepend_whitespace=prepend_space)
    }}''').render(attributes=attributes, prepend_space=prepend_space)

    assert rendered_attributes == expected
{% endraw %}
