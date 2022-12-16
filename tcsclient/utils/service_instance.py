"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

Description: This module implements simple helper functions for managing service instance objects
"""

import atexit
from pyVim.connect import SmartConnect, Disconnect


def connect(host, user, password, port):
    """
    Determine the most preferred API version supported by the specified server,
    then connect to the specified server using that API version, login and return
    the service instance object.
    """

    service_instance = None

    # form a connection...
    try:
     service_instance = SmartConnect(host=host,
                                     user=user,
                                     pwd=password,
                                     port=port,
                                     disableSslCertValidation=True)

     # doing this means you don't need to remember to disconnect your script/objects
     atexit.register(Disconnect, service_instance)
    except IOError as io_error:
        print(io_error)
    except Exception as err:
        print(err)

    if not service_instance:
        raise SystemExit("Unable to connect to host with supplied credentials.")

    return service_instance
