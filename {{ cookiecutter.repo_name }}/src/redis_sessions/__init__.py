import json
import time
import uuid
from collections.abc import MutableMapping

from pyramid.decorator import reify
from pyramid.interfaces import ISession
from zope.interface import implementer

from redis import StrictRedis


@implementer(ISession)
class RedisSession(MutableMapping):
    def __init__(self, data, new=False, created=None):
        self._data = data
        if created is None:
            created = int(time.time())

        self.new = new
        self.modified = False
        self.created = created

    def __setitem__(self, key, value):
        self.changed()
        self._data[key] = value

    def __delitem__(self, key):
        self.changed()
        del self._data[key]

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def changed(self):
        self.modified = True

    def invalidate(self):
        self.clear()
        self.new = True

    def _flash_key(self, queue):
        if not queue:
            return "flash"

        return f"flash.{queue}"

    def flash(self, msg, queue="", allow_duplicate=True):
        queue = self.setdefault(self._flash_key(queue), [])
        if not allow_duplicate and msg in queue:
            return
        queue.append(msg)

    def pop_flash(self, queue=""):
        return self.pop(self._flash_key(queue), [])

    def peek_flash(self, queue=""):
        return self.get(self._flash_key(queue), [])


def _generate_session_key():
    return str(uuid.uuid4())


class RedisSessionFactory:
    redis_client = StrictRedis
    key_generator = staticmethod(_generate_session_key)

    def __init__(
        self,
        url,
        cookie_name="session",
        cookie_max_age=None,
        cookie_path="/",
        cookie_domain=None,
        cookie_secure=False,
        cookie_httponly=True,
        redis_prefix="session.",
        expiration=1200,
        serialize=json.dumps,
        deserialize=json.loads,
    ):
        self.url = url
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.redis_prefix = redis_prefix
        self.expiration = expiration
        self.serialize = serialize
        self.deserialize = deserialize

    @reify
    def redis(self):
        return self.redis_client.from_url(self.url)

    def _session_finalizer(self, request, response):
        session = request.session

        try:
            session_id = request.cookies[self.cookie_name]
        except KeyError:
            session_id = self.key_generator()
        else:
            # If the session is new and we have a session id,
            # delete the old session from redis
            if session.new:
                del self.redis[self.redis_prefix + session_id]
                session_id = self.key_generator()

        if session.modified or session.new:
            serialized_session = self.serialize(
                dict(data=dict(session), created=session.created)
            )
            self.redis.set(
                self.redis_prefix + session_id, serialized_session, ex=self.expiration
            )

        response.set_cookie(
            self.cookie_name,
            session_id,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
        )

    def __call__(self, request):
        request.add_response_callback(self._session_finalizer)

        try:
            session_id = request.cookies[self.cookie_name]
            serialized_session = self.redis[self.redis_prefix + session_id]
            session_data = self.deserialize(serialized_session)
        except (KeyError, ValueError, TypeError):
            return RedisSession({}, new=True)
        else:
            return RedisSession(
                session_data["data"], new=False, created=session_data["created"]
            )


def _parse_settings(settings, maybe_dotted, prefix="session.redis."):
    settings = {
        key[len(prefix) :]: value
        for key, value in settings.items()
        if key.startswith(prefix)
    }

    for setting in ("serialize", "deserialize"):
        if setting not in settings:
            continue
        settings[setting] = maybe_dotted(settings[setting])

    return settings


def includeme(config):
    settings = config.registry.settings
    settings = _parse_settings(config.registry.settings, config.maybe_dotted)

    config.set_session_factory(RedisSessionFactory(**settings))
