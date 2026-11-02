# -*- coding: utf-8 -*-
# Connection handling with python-oracledb for the modules of
# opitzconsulting.ansible_oracle.
# python-oracledb is used in thick mode (Oracle Client libraries) like cx_Oracle before,
# so connections with an Oracle wallet and the settings from sqlnet.ora keep working.
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import traceback

from ansible.module_utils.basic import missing_required_lib

try:
    import oracledb
except ImportError:
    oracledb = None
    HAS_ORACLEDB = False
    ORACLEDB_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_ORACLEDB = True
    ORACLEDB_IMPORT_ERROR = None


def _auth_mode_sysdba():
    # AUTH_MODE_SYSDBA is the new name, SYSDBA is kept for compatibility
    return getattr(oracledb, 'AUTH_MODE_SYSDBA', None) or oracledb.SYSDBA


def oracledb_init(module):
    """Check the import of python-oracledb and enable the thick mode.

    Calls module.fail_json() on errors.
    """
    if not HAS_ORACLEDB:
        module.fail_json(
            msg=missing_required_lib('oracledb'), exception=ORACLEDB_IMPORT_ERROR
        )

    try:
        oracledb.init_oracle_client()
    except oracledb.Error as exc:
        (error,) = exc.args
        module.fail_json(
            msg=(
                'Could not initialize the Oracle Client libraries for '
                'python-oracledb (thick mode) - %s. Make sure ORACLE_HOME '
                '& LD_LIBRARY_PATH is set' % error.message
            ),
            changed=False,
        )


def oracledb_connect(module, hostname, port, service_name, user, password, mode):
    """Connect to the database with python-oracledb in thick mode.

    - neither user nor password: Oracle wallet with the TNS alias service_name
    - user and password: host, port and service_name
    - mode: 'sysdba' or 'normal'

    Returns the connection. Calls module.fail_json() on errors.
    """
    oracledb_init(module)

    params = {}
    if mode == 'sysdba':
        params['mode'] = _auth_mode_sysdba()

    connect = None
    try:
        if not user and not password:
            # If neither user or password is supplied,
            # the use of an oracle wallet is assumed
            connect = '/@%s' % service_name
            conn = oracledb.connect(dsn=service_name, externalauth=True, **params)

        elif user and password:
            connect = oracledb.makedsn(
                host=hostname, port=port, service_name=service_name
            )
            conn = oracledb.connect(user=user, password=password, dsn=connect, **params)

        else:
            module.fail_json(msg='Missing username or password for oracledb')

    except oracledb.Error as exc:
        (error,) = exc.args
        module.fail_json(
            msg='Could not connect to database - %s, connect descriptor: %s'
            % (error.message, connect),
            changed=False,
        )

    return conn
