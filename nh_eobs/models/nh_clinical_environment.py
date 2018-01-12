# -*- coding: utf-8 -*-
import logging

from openerp.models import AbstractModel
from os import environ

_logger = logging.getLogger(__name__)


class NhClinicalEnvironment(AbstractModel):
    """
    A model that provides information about the environment that eObs is
    running in.

    The model was created to fulfil the need to access server environment
    variables from the Javascript (e.g. getting eObs version to display in the
    'about' menu item on desktop).

    From Javascript there are 2 options for server communication:
        * Call model methods.
        * Call an RPC or regular HTTP endpoint.

    Calling a model seemed the better option as backend code could then also
    make use of it without having to unnecessarily call an endpoint.
    """
    _name = 'nh.clinical.environment'

    version = environ.get('VERSION')
    if version is None:
        message = "There is no VERSION environment variable set. " \
                  "Users will not be able to see which version they are " \
                  "using in the UI."
        _logger.warn(message)
    else:
        message = "VERSION environment variable is set to {}.".format(
            version)
        _logger.info(message)

    @staticmethod
    def get_version(*args):
        """
        Returns the current `VERSION` environment variable value, usually
        baked into a Docker image at build time.

        :param args:
        :return: The value of the `VERSION` environment variable.
        :rtype: str
        """
        version = environ.get('VERSION')
        return version
