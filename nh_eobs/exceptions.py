# -*- coding: utf-8 -*-
class StaleDataException(Exception):
    """
    Exception used to inform the user that their current UI state is stale.
    """
    def __init__(self,
                 msg="The data on this page is out of date, please reload.",
                 title="Page Reload Required"):
        super(StaleDataException, self).__init__(msg, title)
