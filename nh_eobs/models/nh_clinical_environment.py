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
from os import environ

from openerp.models import AbstractModel


class NhClinicalEnvironment(AbstractModel):
    _name = 'nh.clinical.environment'

    @staticmethod
    def get_eobs_version(*args):
        try:
            eobs_version = environ['EOBS_VERSION']
            return eobs_version
        except:
            message = "There is no EOBS_VERSION environment variable set!"
            raise KeyError(message)
