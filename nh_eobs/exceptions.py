# -*- coding: utf-8 -*-
class StaleDataException(Exception):

    def __init__(self,
                 msg="The data on this page is out of date, please reload.",
                 title="Page Reload Required"):
        super(StaleDataException, self).__init__(msg, title)
