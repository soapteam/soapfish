# -*- coding: utf-8 -*-

import logging
import traceback

import six

from . import core

logger = logging.getLogger(__name__)


class ExceptionToSoapFault():
    def __init__(self, return_tb=False):
        self.return_tb = return_tb

    def __call__(self, request, next_call):
        try:
            return next_call(request)
        except Exception:
            message = "Internal Error" if not self.return_tb else traceback.format_exc()
            if six.PY2:
                message = message.decode("utf8")
            return core.SOAPError(request.dispatcher.service.version.Code.SERVER, message)


class ExceptionLogger():
    def __init__(self, logger=None, exceptions=(Exception,)):
        self.exceptions = exceptions
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def __call__(self, request, next_call):
        try:
            return next_call(request)
        except self.exceptions as ex:
            self.logger.exception(ex)
            raise
