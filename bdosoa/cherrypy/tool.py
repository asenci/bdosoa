"""
CherryPy tools
"""

import cherrypy


class SQLAlchemyTool(cherrypy.Tool):
    """The SA tool is responsible for associating a SA session
    to the SA engine and attaching it to the current request.
    Since we are running in a multi-threaded application,
    we use the scoped_session that will create a session
    on a per thread basis so that you don't worry about
    concurrency on the session object itself.

    This tools binds a session to the engine each time
    a requests starts and commits/rollbacks whenever
    the request terminates.
    """

    def __init__(self):
        super(SQLAlchemyTool, self).__init__(
            'on_start_resource', self.on_start_resource, priority=20)

    def _setup(self):
        super(SQLAlchemyTool, self)._setup()

        cherrypy.request.hooks.attach(
            'on_end_resource', self.on_end_resource, priority=80)

    # noinspection PyMethodMayBeStatic
    def on_start_resource(self):
        """Attaches a session to the requests scope by requesting
        the SA plugin to bind a session to the SA engine.
        """

        cherrypy.log.error('Binding session.', 'TOOLS.SQLALCHEMY', 10)
        req_session = cherrypy.engine.publish('sqlalchemy_get_session')
        cherrypy.request.db = req_session.pop()

    # noinspection PyMethodMayBeStatic
    def on_end_resource(self):
        """Commits the current transaction or rolls back
        if an error occurs. Removes the session handle
        from the requests scope.
        """

        if hasattr(cherrypy.request, 'db'):
            cherrypy.log.error('Committing session.', 'TOOLS.SQLALCHEMY', 10)

            try:
                cherrypy.request.db.commit()

            except:
                cherrypy.request.db.rollback()
                raise

            finally:
                cherrypy.request.db.remove()
                cherrypy.request.db = None

