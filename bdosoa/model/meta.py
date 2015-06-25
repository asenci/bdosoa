"""
bdosoa - SQLAlchemy helper code
"""

import cherrypy
import sqlalchemy.ext.declarative
import sqlalchemy.orm


# noinspection PyUnresolvedReferences
class Base(object):
    """Base ORM model"""

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True,
                           nullable=False, autoincrement=True)

Base = sqlalchemy.ext.declarative.declarative_base(cls=Base)
Base.metadata.naming_convention = {
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s'
}


# noinspection PyDocstring
def create_engine(configuration=cherrypy.config, prefix='sqlalchemy.', **kwargs):
    """Create a new Engine instance using a dictionary (CherryPy configuration
     dictionary by default)

    :param dict configuration: a dictionary with prefixed keys
    :param str prefix: key prefix on the dictionary
    :return: an Engine instance
    :rtype: Engine
    """

    return sqlalchemy.engine_from_config(configuration, prefix, **kwargs)


# noinspection PyPep8Naming
class scoped_session(sqlalchemy.orm.scoped_session):
    """Provides scoped management of Session objects

    :param session_factory: a factory to create new Session instances.
     This is usually, but not necessarily, an instance of sessionmaker.
    :param scopefunc: optional function which defines the current scope.
     Defaults to returning the current CherryPy Request object.
    """

    def __init__(self, session_factory,
                 scopefunc=lambda: cherrypy.serving.request):

        super(scoped_session, self).__init__(session_factory, scopefunc)


sessionmaker = sqlalchemy.orm.sessionmaker

NoResultFound = sqlalchemy.orm.exc.NoResultFound
