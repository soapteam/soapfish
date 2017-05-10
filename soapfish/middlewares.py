# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import traceback

import six

from . import core


class ExceptionToSoapFault(object):

    def __init__(self, traceback=False):
        self.traceback = traceback

    def __call__(self, request, next_call):
        try:
            return next_call(request)
        except Exception as e:
            if self.traceback:
                message = traceback.format_exc()
            else:
                message = '%s: %s' % (e.__class__.__name__, e)
            if six.PY2:
                message = message.decode('utf8')
            return core.SOAPError(request.dispatcher.service.version.Code.SERVER, message)


class ExceptionLogger(object):

    def __init__(self, logger=None, exceptions=(Exception,), traceback=True):
        if not isinstance(exceptions, tuple):
            raise TypeError('exceptions must be a tuple.')
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.traceback = traceback
        self.exceptions = exceptions

    def __call__(self, request, next_call):
        try:
            return next_call(request)
        except self.exceptions as e:
            if self.traceback:
                self.logger.exception(e)
            else:
                self.logger.error('%s: %s', e.__class__.__name__, e)
            raise e
