from pyramid.config import Configurator
from pyramid.events import ApplicationCreated, NewRequest, subscriber
from pyramid.httpexceptions import HTTPFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.view import view_config

import os
import sqlite3

here = os.environ['OPENSHIFT_APP_DIR']

#===============================================================================
#
# This example was taken from
#
# http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/
#                                        single_file_tasks/single_file_tasks.html
#
#===============================================================================

#===============================================================================
# The Pyramid Views
#===============================================================================


@view_config(route_name='list', renderer='list.mako')
def list_view(request):
    '''
    List a bunch of todo items.

    request -- The request object.
    '''
    rs = request.db.execute("select id, name from tasks where closed = 0")
    tasks = [dict(id=row[0], name=row[1]) for row in rs.fetchall()]
    return {'tasks': tasks}


@view_config(route_name='new', renderer='new.mako')
def new_view(request):
    '''
    Insert a new entry in the db.

    request -- The request object.
    '''
    if request.method == 'POST':
        if request.POST.get('name'):
            request.db.execute('insert into tasks (name, closed) values (?, ?)',
                               [request.POST['name'], 0])
            request.db.commit()
            request.session.flash('New task was successfully added!')
            return HTTPFound(location=request.route_url('list'))
        else:
            request.session.flash('Please enter a name for the task!')
    return {}


@view_config(route_name='close')
def close_view(request):
    '''
    Resolve an open todo item.

    request -- The request object.
    '''
    task_id = int(request.matchdict['id'])
    request.db.execute("update tasks set closed = ? where id = ?", (1, task_id))
    request.db.commit()
    request.session.flash('Task was successfully closed!')
    return HTTPFound(location=request.route_url('list'))


@view_config(context='pyramid.exceptions.NotFound', renderer='notfound.mako')
def notfound_view(self):
    '''
    Do this on 404 errors :-)
    '''
    return {}

#===============================================================================
# The pyramid subscribers
#===============================================================================


@subscriber(NewRequest)
def new_request_subscriber(event):
    '''
    The entry point.

    event -- An event.
    '''
    request = event.request
    settings = request.registry.settings
    request.db = sqlite3.connect(settings['db'])
    request.add_finished_callback(close_db_connection)


def close_db_connection(request):
    '''
    Close the sqllite connection.

    request -- The request object.
    '''
    request.db.close()


@subscriber(ApplicationCreated)
def application_created_subscriber(event):
    '''
    When the application is created - make a new clean db.

    event - An event.
    '''
    f = open(os.path.join(here, '..', 'data', 'schema.sql'), 'r')
    stmt = f.read()
    settings = event.app.registry.settings
    db = sqlite3.connect(settings['db'])
    db.executescript(stmt)
    db.commit()
    f.close()

#===============================================================================
# The WSGI part...
#===============================================================================


def application(environ, start_response):
    '''
    A WSGI application.

    Configure pyramid, add routes and finally server the app.
    '''
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    settings['mako.directories'] = os.path.join(here, 'static')
    settings['db'] = os.path.join(here, '..', 'data', 'tasks.db')

    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

    config = Configurator(settings=settings, session_factory=session_factory)

    config.add_route('list', '/')
    config.add_route('new', '/new')
    config.add_route('close', '/close/{id}')

    config.add_static_view('static', os.path.join(here, 'static'))

    config.scan()

    return config.make_wsgi_app()(environ, start_response)
