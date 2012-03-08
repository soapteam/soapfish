# -*- coding: utf-8 -*-
################################################################################

'''
Soapbox Configuration
'''

################################################################################
# HTTP


# Maximum permitted time for a request to complete (seconds):
REQUEST_TIMEOUT = 30

# Location of the CA certificates to be used by httplib2:
# Note: This is the system-wide default location on Ubuntu.
CA_CERTIFICATE_FILE = '/etc/ssl/certs/ca-certificates.crt'


################################################################################
# Flags


# For deciding whether to validate against schemas when parsing:
VALIDATE_ON_PARSE = True


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4 Flags
