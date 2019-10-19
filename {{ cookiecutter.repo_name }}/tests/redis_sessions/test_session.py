import pytest

from redis_sessions import RedisSession


@pytest.fixture
def existing_session():
    return RedisSession({
        'a': 123
    }, new=False)


def test_session_flash(existing_session):
    existing_session.flash("Hello, world")

    assert 'flash' in existing_session
    assert existing_session['flash'] == ['Hello, world'], "Flash message wasn't flashed"


def test_session_flash_allows_duplicates(existing_session):
    existing_session.flash('Hello')
    existing_session.flash('Hello')
    assert 'flash' in existing_session
    assert existing_session['flash'] == ['Hello', 'Hello']


def test_session_flash_disallows_duplicates(existing_session):
    existing_session.flash('Hello')
    existing_session.flash('Hello', allow_duplicate=False)
    assert 'flash' in existing_session
    assert existing_session['flash'] == ['Hello']


def test_session_flash_queue(existing_session):
    existing_session.flash('Hello', 'queue')
    assert 'flash.queue' in existing_session
    assert existing_session['flash.queue'] == ['Hello']


def test_session_invalidate(existing_session):
    existing_session.invalidate()

    assert existing_session.new is True, "Invalidate didn't cause session to be marked new"
    assert 'a' not in existing_session


def test_session_pop_flash(existing_session):
    existing_session.flash('test flash', 'queue')
    existing_session.flash('another test flash')

    assert existing_session.pop_flash('queue') == ['test flash']
    assert existing_session.pop_flash() == ['another test flash']


def test_session_peek_flash(existing_session):
    existing_session.flash('test flash', 'queue')
    existing_session.flash('another test flash')

    assert existing_session.peek_flash('queue') == ['test flash']
    assert existing_session.peek_flash() == ['another test flash']


def test_session_pop_flash_nonexistant(existing_session):
    assert existing_session.pop_flash('queue') == []
    assert existing_session.pop_flash() == []


def test_session_peek_flash_nonexistant(existing_session):

    assert existing_session.peek_flash('queue') == []
    assert existing_session.peek_flash() == []
