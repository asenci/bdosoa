"""
BDOSOA - BDD importing utility
"""

import cherrypy
import logging
import sqlalchemy
import sqlalchemy.orm
import sys

from csv import DictReader
from datetime import datetime
from optparse import OptionParser

from bdosoa.model import Base, ServiceProviderGateway, SubscriptionVersion
from bdosoa.model.meta import NoResultFound


def format_date(timestamp):
    dt = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def format_version_id(version_id):
    return int(version_id)


BDD_DELIMITER = '|'

BDD_HEADER = (
    'subscription_version_id',
    'subscription_version_tn',
    'subscription_rn1',
    'subscription_recipient_sp',
    'subscription_recipient_eot',
    'subscription_activation_timestamp',
    'subscription_lnp_type',
    'subscription_download_reason',
    'subscription_line_type',
    'subscription_new_cnl',
)

BDD_MAPS = {
    'subscription_lnp_type': {
        '': '',
        '0': 'lspp',
        '1': 'lisp',
    },
    'subscription_download_reason': {
        '': '',
        '0': 'new',
        '1': 'delete',
        '2': 'modified',
    },
    'subscription_line_type': {
        '': '',
        '1': 'Basic',
        '2': 'DDR',
        '3': 'CNG',
    },
}


def main(args=None):
    opts = OptionParser(usage='usage: %prog [options] file ..')
    opts.add_option('-c', '--config', action='append',
                    help='specify config file', default=[])
    opts.add_option('-d', '--debug', action='store_true', default=False,
                    help='enable debug messages')
    opts.add_option('-q', '--quiet', action='store_true', default=False,
                    help='only log warnings and errors')
    opts.add_option('-s', '--spid', help='Service Provider ID')
    opts.add_option('-t', '--token', help='Authentication token')

    options, args = opts.parse_args(args)

    if not (options.spid and options.token):
        opts.error('You must specify the Service Provider ID and '
                   'Authentication token')

    # Set logging level
    if options.debug and options.quiet:
        opts.error('You may only specify one of the debug, quiet options')

    log_format = '%(asctime)s <%(name)s:%(levelname)s> %(message)s'
    if options.debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    elif options.quiet:
        logging.basicConfig(level=logging.ERROR, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    logger = logging.getLogger(__package__)
    logger.debug('Debugging enabled.')

    logger.debug('Reading configuration files: {0}'
                 .format(', '.join(options.config)))

    # Merge configuration files
    for c in options.config:
        cherrypy.config.update(c)

    logger.debug('Creating SQLAlchemy engine.')
    db_engine = sqlalchemy.engine_from_config(cherrypy.config)

    if cherrypy.config.get('sqlalchemy_create_all', False):
        logger.info('Creating SQLAlchemy database schemas.')
        Base.metadata.create_all(db_engine)

    DBSession = sqlalchemy.orm.sessionmaker(bind=db_engine)
    db_session = None

    for cvs_file in args or [sys.stdin]:
        row_count = 0

        try:
            if isinstance(cvs_file, (str, unicode)):
                cvs_file = open(cvs_file)

            logger.info('Processing file: {0}'.format(cvs_file.name))

            db_session = DBSession()

            try:
                spg = db_session.query(ServiceProviderGateway).filter_by(
                    service_provider_id=options.spid,
                    token=options.token,
                    enabled=True,
                ).one()

            except NoResultFound:
                raise RuntimeError('Authentication error')

            reader = DictReader(cvs_file, fieldnames=BDD_HEADER,
                                delimiter=BDD_DELIMITER,
                                strict=True)

            for row in reader:
                for key, value_map in BDD_VALUE_MAPS.items():
                    if callable(value_map):
                        row[key] = value_map(row[key])
                    else:
                        row[key] = value_map[row[key]]

                # Create a new subscription version
                db_session.add(SubscriptionVersion(
                    service_provider_gateway_id=spg.id, **row))

                logger.debug('New subscription version: {0}'
                             .format(row['subscription_version_id']))

                # Flush every 10.000 rows
                if row_count >= 10000:
                    logger.warn('Flushing database session.')
                    db_session.flush()
                    row_count = 0
                else:
                    row_count += 1

            # Commit database session
            try:
                logger.debug('Committing database session.')
                db_session.commit()
            except:
                logger.exception('Error committing database session.')
                db_session.rollback()
                raise
            finally:
                db_session.close()
                db_session = None

        except:
            logger.exception('Error processing file: {0}'
                             .format(cvs_file.name))
            if db_session:
                logger.debug('Rolling back database session.')
                db_session.rollback()
                db_session.close()
            break

        finally:
            logger.info('Done processing file: {0}'.format(cvs_file.name))
            cvs_file.close()


if __name__ == '__main__':
    main()
