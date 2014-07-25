"""
bdosoa - SQLAlchemy helper code
"""

import cherrypy

from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound


# noinspection PyUnresolvedReferences
class Base(object):
    """Base ORM model"""

    NoResultFound = NoResultFound

    id = Column(Integer, primary_key=True)

    @classmethod
    def all(cls):
        """Get all objects

        :return: All model objects
        :rtype: list
        """

        return Session.query(cls).all()

    @classmethod
    def create(cls, *args, **kwargs):
        """Create a new object

        :param args: Arguments
        :param kwargs: Keyword arguments
        :return: The object
        :rtype: Base
        """

        obj = cls(*args, **kwargs)
        Session.add(obj)
        Session.flush()

        return obj

    @classmethod
    def filter_by(cls, **kwargs):
        """Filter objects by attributes

        :param kwargs: Attributes
        :return: A list of objects
        :rtype: list
        """

        return Session.query(cls).filter_by(**kwargs)

    @classmethod
    def get_by(cls, **kwargs):
        """Get an object by its attributes

        :param kwargs: Attributes
        :return: An object
        :rtype: Base
        :raise MultipleResultsFound: If more than one object matches the filter
        """

        return cls.filter_by(**kwargs).one()

    @classmethod
    def get(cls, ident):
        """Get an object by its id

        :param ident: Object id
        :type ident: str or int
        :return: An object
        :rtype: Base
        """

        return Session.query(cls).get(ident)

Base = declarative_base(cls=Base)
Base.metadata.naming_convention = {
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s'
}


# noinspection PyUnresolvedReferences
class Session(scoped_session):
    """SQLAlchemy session"""

    def __init__(self):
        super(Session, self).__init__(
            sessionmaker(), lambda: cherrypy.serving.request)

    def cleanup_hook(self):
        """Commit scoped session"""

        cherrypy.log.error('Commit invoked for session: {0!r}'.format(
            Session()), 'ENGINE', severity=10)

        try:
            self.commit()
        except:
            self.rollback()
            raise
        finally:
            self.remove()

    def config_handler(self, key, value):
        """Handle config attributes

        :param str key: attribute name
        :param str value: attribute value
        """

        if key == 'url':
            self.configure(bind=create_engine(value))
            cherrypy.log.error('Configured database access string.', 'ENGINE')

        elif key == 'create':
            if value is True:
                Base.metadata.create_all(Session.get_bind())
                cherrypy.log.error('Created database tables.', 'ENGINE')

        else:
            cherrypy.log.error('Configuration directive not implemented: {0}'
                               .format(key), 'ENGINE')

Session = Session()
