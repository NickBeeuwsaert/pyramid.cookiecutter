import json
import random
import uuid

import pytest
from pyramid import testing

from redis_sessions import RedisSession, RedisSessionFactory, _generate_session_key


class DummyRedis(object):
    def __init__(self, db):
        self.db = db

    def set(self, key, name, ex=None):
        self.db[key] = name

    def __getitem__(self, key):
        return self.db[key]

    def __delitem__(self, key):
        self.db.pop(key, None)

    def from_url(self, url):
        return self

    def __contains__(self, item):
        return item in self.db


@pytest.fixture
def redis_client():
    return DummyRedis({
        'session.a': """{
            "data": {
                "some_data": "123",
                "more_data": 456
            },
            "created": 0
        }""",
        'session.b': "5",
        'session.c': 5
    })


@pytest.fixture
def key_func():
    it = iter(['aa', 'bb', 'cc'])
    return lambda: next(it)


@pytest.fixture
def session_factory(key_func, redis_client):
    factory = RedisSessionFactory(
        url='redis:///',
        cookie_name='session'
    )

    factory.key_generator = key_func
    factory.redis_client = redis_client

    return factory


def test_creates_new_session_on_empty_cookie(session_factory, redis_client):
    request = testing.DummyRequest()
    request.session = session_factory(request)

    assert isinstance(request.session, RedisSession), "Session factory did not return a RedisSession"
    assert request.session.new, "Session is not marked as new"

    request.session['test_data'] = '1234'

    response = request.response
    for cb in request.response_callbacks:
        cb(request, response)

    assert 'session.aa' in redis_client
    assert json.loads(redis_client['session.aa']).get('data') == {'test_data': '1234'}


def test_creates_new_session_on_invalid_cookie(session_factory, redis_client):
    request = testing.DummyRequest(cookies={
        'session': 'non-existant'
    })
    request.session = session_factory(request)

    assert isinstance(request.session, RedisSession), "Session factory failed to return a Redis Session"
    assert request.session.new, "Session is not marked as new"

    request.session['some_data'] = '123'

    response = request.response
    for cb in request.response_callbacks:
        cb(request, response)

    assert 'session.aa' in redis_client
    assert json.loads(redis_client['session.aa']).get('data') == {'some_data': '123'}


def test_creates_new_session_on_invalid_data(session_factory, redis_client):
    request = testing.DummyRequest(cookies={
        'session': 'c'
    })
    request.session = session_factory(request)

    assert isinstance(request.session, RedisSession), "Session factory failed to return a Redis Session"
    assert request.session.new, "Session is not marked as new"

    request.session['bunk_data'] = [1, 2, 3]

    response = request.response
    for cb in request.response_callbacks:
        cb(request, response)

    assert 'session.c' not in redis_client, "Old session ID not deleted"
    assert 'session.aa' in redis_client
    assert json.loads(redis_client['session.aa']).get('data') == {'bunk_data': [1, 2, 3]}


def test_fetches_existing_session(session_factory, redis_client):
    request = testing.DummyRequest(cookies={
        'session': 'a'
    })
    request.session = session_factory(request)

    assert isinstance(request.session, RedisSession), "Session factory failed to return a Redis Session"
    assert request.session.new is False, "Exising session should not be marked new"

    assert dict(request.session) == {'some_data': '123', 'more_data': 456}

    response = request.response
    for cb in request.response_callbacks:
        cb(request, response)

    assert 'session.a' in redis_client, "Session key not there after save"
    assert json.loads(redis_client['session.a']).get('data') == {'some_data': "123", "more_data": 456}


def test_saves_modified_session(session_factory, redis_client):
    request = testing.DummyRequest(cookies={
        'session': 'a'
    })
    request.session = session_factory(request)

    assert isinstance(request.session, RedisSession), "Session factory failed to return a Redis Session"
    assert request.session.new is False, "Session loaded from redis marked as new"

    assert dict(request.session) == {'some_data': '123', 'more_data': 456}
    request.session['a'] = [1, 2, 3]

    response = request.response
    for cb in request.response_callbacks:
        cb(request, response)

    assert json.loads(redis_client['session.a']).get('data') == {
        'some_data': '123',
        'more_data': 456,
        'a': [1, 2, 3]
    }, "Modified session not saved"


def test_invalidate(session_factory, redis_client):
    request = testing.DummyRequest(cookies={
        'session': 'a'
    })
    request.session = session_factory(request)

    assert isinstance(request.session, RedisSession), "Session factory failed to return a Redis Session"
    assert request.session.new is False, "Session loaded from redis marked as new"

    request.session.invalidate()
    request.session['data'] = 123

    response = request.response
    for cb in request.response_callbacks:
        cb(request, response)

    assert 'session.a' not in redis_client
    assert 'session.aa' in redis_client
    assert json.loads(redis_client['session.aa']).get('data') == {"data": 123}

def test_sends_cookie_for_new_session(session_factory, redis_client):
    request = testing.DummyRequest()
    request.session = session_factory(request)

    request.session['test'] = 1234

    response = request.response
    for cb in request.response_callbacks:
        cb(request, response)

    cookies = [
        value
        for header, value in response.headerlist
        if header == 'Set-Cookie'
    ]

    assert any(cookie.startswith('session=aa;') for cookie in cookies)

def test_sends_cookie_for_existing_session(session_factory, redis_client):
    request = testing.DummyRequest(cookies={
        'session': 'a'
    })
    request.session = session_factory(request)

    request.session['test'] = 1234

    response = request.response
    for cb in request.response_callbacks:
        cb(request, response)

    cookies = [
        value
        for header, value in response.headerlist
        if header == 'Set-Cookie'
    ]

    assert any(cookie.startswith('session=a;') for cookie in cookies)


def test_sends_cookie_for_existing_unmodified_session(session_factory, redis_client):
    request = testing.DummyRequest(cookies={
        'session': 'a'
    })
    request.session = session_factory(request)

    response = request.response
    for cb in request.response_callbacks:
        cb(request, response)

    cookies = [
        value
        for header, value in response.headerlist
        if header == 'Set-Cookie'
    ]

    assert any(cookie.startswith('session=a;') for cookie in cookies)


def test_default_session_key_generator():
    session_key = uuid.UUID(_generate_session_key())

    assert session_key.variant == uuid.RFC_4122
    assert session_key.version == 4
