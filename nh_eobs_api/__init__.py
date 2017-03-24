# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from json import encoder

from . import controllers
from . import routing

encoder.c_make_encoder = None
encoder.FLOAT_REPR = lambda o: format(o, '.1f')
