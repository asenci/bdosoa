"""
BDOSOA - BDD importing utility
"""

import logging
import sys

from datetime import datetime
from optparse import OptionParser


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
    'service_provider_gateway_id',
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
    opts.add_option('-d', '--debug', action='store_true', default=False,
                    help='enable debug messages')
    opts.add_option('-o', '--output',
                    help='output file')
    opts.add_option('-q', '--quiet', action='store_true', default=False,
                    help='only log warnings and errors')
    opts.add_option('-s', '--spg_id',
                    help='Service Provider Gateway (SPG) ID')

    options, args = opts.parse_args(args)

    if not options.spg_id:
        opts.error('You must specify the Service Provider Gateway (SPG) ID')

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

    if options.output:
        out_file = open(options.output, 'w')
    else:
        out_file = sys.stdout

    # Print header
    out_file.write(','.join(BDD_HEADER) + '\n')

    for in_file in args or [sys.stdin]:
        try:
            if isinstance(in_file, (str, unicode)):
                in_file = open(in_file)

            logger.info('Processing file: {0}'.format(in_file.name))

            for line in in_file:

                row = line.rstrip('\n').split(BDD_DELIMITER)

                out_file.write(','.join((
                    row[0], row[1], row[2], row[3], row[4],
                    datetime.strptime(row[5], '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S'),
                    BDD_MAPS['subscription_lnp_type'][row[6]],
                    BDD_MAPS['subscription_download_reason'][row[7]],
                    BDD_MAPS['subscription_line_type'][row[8]],
                    row[9], options.spg_id,)) + '\n')

        except:
            logger.exception('Error processing file: {0}'
                             .format(in_file.name))
            break

        finally:
            logger.info('Done processing file: {0}'.format(in_file.name))
            in_file.close()

    out_file.close()

if __name__ == '__main__':
    main()
