from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.csrf import SessionCSRFStoragePolicy
from pyramid.request import Request
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from {{cookiecutter.repo_name}}.models.user import User


def db(request: Request):
    session_factory = request.registry['db_factory']
    session = session_factory()

    @request.add_finished_callback
    def cleanup(request):
        if request.exception is not None:
            session.rollback()
        else:
            session.commit()
        session.close()
    
    return session

def user(request: Request):
    userid = request.unauthenticated_userid

    if userid is not None:
        return request.db.query(User).get(userid)

    return userid

def main(global_config, **settings):
    settings.setdefault('tm.manager_hook', 'pyramid_tm.explicit_manager')
    config = Configurator(
        settings=settings,
        authentication_policy=SessionAuthenticationPolicy(),
        authorization_policy=ACLAuthorizationPolicy(),
    )
    config.set_csrf_storage_policy(SessionCSRFStoragePolicy())

    config.include("pyramid_tm")
    config.include("pyramid_retry")
    config.include("pyramid_jinja2")

    config.include("redis_sessions")

    config.include(".views")

    # Configure Jinja2
    config.add_jinja2_search_path("{{ cookiecutter.repo_name }}:templates")

    # Set up the database
    engine = engine_from_config(settings, 'sqlalchemy.')
    session_factory = sessionmaker(bind=engine)
    config.registry['db_factory'] = session_factory
    config.add_request_method(db, 'db', reify=True)
    config.add_request_method(user, 'user', reify=True)

    return config.make_wsgi_app()
