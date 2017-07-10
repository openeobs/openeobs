# -*- coding: utf-8 -*-
"""
A module that provides information about the environment that eObs is running
in.

The module was created to fulfil the need to access server environment
variables from the Javascript (e.g. getting eObs version to display in the
'about' menu item on desktop).

From Javascript there are 2 options for server communication:
    * Call model methods.
    * Call an RPC or regular HTTP endpoint.

Calling a model seemed the better option as backend code could then also make
use of it without having to unnecessarily call an endpoint.
"""
import logging
from os import environ

from openerp.models import AbstractModel


_logger = logging.getLogger(__name__)


class NhClinicalEnvironment(AbstractModel):
    _name = 'nh.clinical.environment'

    @staticmethod
    def get_eobs_version(*args):
        eobs_version = environ.get('EOBS_VERSION')
        if eobs_version is None:
            message = "There is no EOBS_VERSION environment variable set. " \
                      "Users will not be able to see which version they are " \
                      "using in the UI."
            _logger.warn(message)
        return eobs_version
