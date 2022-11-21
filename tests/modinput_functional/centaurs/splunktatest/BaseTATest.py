#!/usr/bin/python
"""
Meta
====
    $Id$  # nopep8
    $DateTime$
    $Author$
    $Change$
"""

import os
import logging

try:
    from StringIO import StringIO  ## for Python 2
except ImportError:
    from io import StringIO  ## for Python 3
import pytest
from pytest_splunk_addon.helmut.log import HelmutFormatter
from pytest_splunk_addon.helmut.log import _LOG_FORMAT as LOG_FORMAT

from tacommon.ta_rest import get_session_key
from tacommon.splunk_instance_manager import SplunkInstanceManager, SplunkInstance

LOGGER = logging.getLogger(__name__)
LOG_BUFFER = StringIO()
LOG_HANDLER = logging.StreamHandler(LOG_BUFFER)
LOG_HANDLER.setFormatter(HelmutFormatter(LOG_FORMAT))
TIMEOUT = 60
POLL_FREQUENCY = 10

LOGGER.addHandler(LOG_HANDLER)
LOG_HANDLER.setLevel(logging.DEBUG)


class BaseTATest:
    """
    Base TA test cases setup
    """

    logger = LOGGER
    splunk = None
    session_key = None
    rest = None
    username = None
    password = None
    config_file = None
    splunk_home = None
    splunk_url = None
    splunkd_port = "8089"
    remote = None
    splunk_instance_manager = None

    TA_APP_NAME = "Splunk_TA_dummy"
    TA_APP_USER = "nobody"

    @classmethod
    def setup_class(cls):
        """
        Setup Class to run before each session.
        """
        # Logger
        cls.logger.debug("x" * 80)
        cls.logger.debug("CLASS SETUP")
        cls.logger.debug("x" * 80)

        # Splunk
        cls.logger.info("Setting up splunk instance in setup class.")

        if not cls.splunk_instance_manager:
            si = SplunkInstance(cls.splunk)
            si.username = cls.username
            si.password = cls.password
            si.splunk_url = cls.splunk_url
            si.splunk_home = cls.splunk_home
            si.splunkd_port = cls.splunkd_port
            cls.splunk_instance_manager = SplunkInstanceManager({}, si)

        cls.splunk = cls.splunk_instance_manager.searchhead_splunk.splunk
        cls.forwarder_splunk_instance = cls.splunk_instance_manager.forwarder_splunk
        cls.splunk_home = cls.forwarder_splunk_instance._splunk_home
        cls.rest = cls.splunk_instance_manager.forwarder_splunk.rest

        # session_key, for raw rest api handling
        cls.splunk_url = (
            "https://"
            + cls.forwarder_splunk_instance.splunk_url
            + ":"
            + cls.forwarder_splunk_instance.splunkd_port
        )
        cls.logger.info(
            "Setting up session_key in setup class to url %s", cls.splunk_url
        )
        cls.session_key = cls.get_splunk_session_key(
            cls.splunk_url,
            cls.forwarder_splunk_instance.username,
            cls.forwarder_splunk_instance.password,
        )

    @classmethod
    def teardown_class(cls):
        """
        Teardown Class to run after each session.
        """
        cls.logger.debug("x" * 80)
        cls.logger.debug("CLASS TEARDOWN")
        cls.logger.debug("x" * 80)

    @classmethod
    def get_config_credential(cls):
        pass

    @staticmethod
    def get_splunk_session_key(splunk_url, username, password):
        return get_session_key(splunk_url, username, password)

    @classmethod
    def get_ta_build_number(cls):
        return "UNKNOWN"

    def setup_method(self, method):
        """
        Setup Method to run before each test case
        """
        LOG_BUFFER.truncate(0)
        LOG_BUFFER.seek(0)

        self.logger = BaseTATest.logger
        self.test_name = method.__name__
        self.logger.info("=" * 80)
        self.logger.info("START test case: %s" % self.test_name)
        self.logger.info("-" * 80)

    def teardown_method(self, method):
        """
        Setup Method to run after each test case
        """
        self.logger.info("")
        self.logger.info("-" * 80)
        self.logger.info(f"END case: {self.test_name}")
        self.logger.info("=" * 80)
        self.logger.info("")
