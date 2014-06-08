from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound


class Base(object):
    NoResultFound = NoResultFound

    id = Column(Integer, primary_key=True)

    @classmethod
    def all(cls):
        return Session.query(cls).all()

    @classmethod
    def create(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        Session.add(obj)
        Session.flush()
        return obj

    @classmethod
    def filter_by(cls, **kwargs):
        return Session.query(cls).filter_by(**kwargs)

    @classmethod
    def get_by(cls, **kwargs):
        return cls.filter_by(**kwargs).one()

    @classmethod
    def get(cls, ident):
        return Session.query(cls).get(ident)
Base = declarative_base(cls=Base)
Base.metadata.naming_convention = {
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s'
}


class Session(scoped_session):

    def __init__(self):
        import cherrypy

        super(Session, self).__init__(
            sessionmaker(), lambda: cherrypy.serving.request)

    def cleanup_hook(self):
        """Commit scoped session"""
        import cherrypy

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
        """Handle config attributes"""
        import cherrypy

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
