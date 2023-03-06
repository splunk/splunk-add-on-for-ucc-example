#
# SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
# SPDX-License-Identifier: LicenseRef-Splunk-8-2021
#
#
from pytest_splunk_addon_ui_smartx.base_test import UccTester
from pytest_splunk_addon_ui_smartx.pages.logging import Logging
import pytest
import time
import re
import random
import os

TA_NAME = "Splunk_TA_UCCExample"
TA_CONF = "splunk_ta_uccexample_settings"

DEFAULT_CONFIGURATION = {"loglevel": "INFO"}


@pytest.fixture(autouse=True)
def reset_configuration(ucc_smartx_rest_helper):
    yield
    logging = Logging(TA_NAME, TA_CONF, ucc_smartx_rest_helper=ucc_smartx_rest_helper)
    logging.backend_conf.update_parameters(DEFAULT_CONFIGURATION)


class TestLogging(UccTester):
    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.logging
    def test_logging_select_random_log_level(
        self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper
    ):
        """This test cases checks the functionality of selecting random log level and verification of the same in UI"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        logging = Logging(
            TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper
        )
        level = random.choice(levels)
        logging.log_level.select(level)
        logging.save()
        self.assert_util(logging.log_level.get_value().lower(), level.lower())
