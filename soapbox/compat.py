# -*- coding: utf-8 -*-
################################################################################

'''
Compatibility for older versions of Python.
'''

################################################################################
# Imports


import logging


################################################################################
# Logging Null Handler


class NullHandler(logging.Handler):
    '''
    '''

    def emit(self, record):
        '''
        '''
        pass


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4 Flags
