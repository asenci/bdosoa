"""
bdosoa - CherryPy application
"""

import cherrypy
import os

from bdosoa.app import soap, sync


class Root(object):
    """Application Root"""

    def __init__(self):
        self.soap = soap.SOAP()
        self.sync = sync.Sync()

    @cherrypy.expose
    def index(self):
        """Index page"""

        return """<html>
          <head></head>
          <body>
            <form method="post" action="query/">
              Query: <input type="text" name="query_string" />
              <button type="submit">Consultar</button>
            </form>
          </body>
        </html>"""

    @cherrypy.expose
    def query(self, query_string):
        """Query BDO SVs

        :param str query_string: Query string
        :return: The query result
        :rtype: str
        """
        # todo: implement SV query

        if cherrypy.request.method != 'POST':
            cherrypy.response.headers['Allow'] = 'POST'
            raise cherrypy.HTTPError(405)

        return query_string

App = cherrypy.Application(Root(), config={
    '/': {
        'tools.sqlalchemy.on': True,
    },
    '/static': {
        'tools.sqlalchemy.on': False,
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(
            os.path.dirname(__file__), '../static'),
    }
})