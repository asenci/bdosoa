"""
CherryPy plugins
"""

import cherrypy

import bdosoa.model.meta


class SQLAlchemyPlugin(cherrypy.process.plugins.SimplePlugin):
    """The plugin is registered to the CherryPy engine and therefore
    is part of the bus (the engine *is* a bus) registery.

    We use this plugin to create the SA engine. At the same time,
    when the plugin starts we create the tables into the database
    using the mapped class of the global metadata.
    """

    engine = None
    scoped_session = None

    def __init__(self, bus, configuration=cherrypy.config,
                 prefix='sqlalchemy.', **kwargs):
        super(SQLAlchemyPlugin, self).__init__(bus)

        self.args = (configuration, prefix)
        self.kwargs = kwargs

    def start(self):
        """Plugin startup routine"""

        self.bus.log('Creating SQLAlchemy engine.')
        self.engine = bdosoa.model.meta.create_engine(
            *self.args, **self.kwargs)

        self.bus.log('Creating SQLAlchemy session registry.')
        self.scoped_session = bdosoa.model.meta.scoped_session(
            bdosoa.model.meta.sessionmaker(self.engine))

        if cherrypy.config.get('sqlalchemy_create_all', True):
            self.bus.log('Creating SQLAlchemy database schemas.')
            bdosoa.model.meta.Base.metadata.create_all(self.engine)

        self.bus.subscribe('sqlalchemy_get_session', self.get_session)

    def stop(self):
        """Plugin shutdown routine"""

        self.bus.unsubscribe('sqlalchemy_get_session', self.get_session)

        if self.scoped_session:
            self.bus.log('Closing SQLAlchemy sessions.')
            self.scoped_session.close_all()
            self.scoped_session = None

        if self.engine:
            self.bus.log('Closing SQLAlchemy engine.')
            self.engine.dispose()
            self.engine = None

    def get_session(self):
        """Returns the session registry to the caller"""

        return self.scoped_session
