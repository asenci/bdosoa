"""
BDOSOA - BDD files processing routines
"""

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


class BDDFile(object):
    __fd__ = None

    def __init__(self, bdd_file):
        if isinstance(bdd_file, (str, unicode)):
            self.__fd__ = open(bdd_file)
        else:
            self.__fd__ = bdd_file

