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

DEFAULT_CONFIGURATION = {
    'loglevel': 'INFO'
}

@pytest.fixture(autouse=True)
def reset_configuration(ucc_smartx_rest_helper):
    yield
    logging = Logging(TA_NAME, TA_CONF, ucc_smartx_rest_helper=ucc_smartx_rest_helper)
    logging.backend_conf.update_parameters(DEFAULT_CONFIGURATION)

class TestLogging(UccTester):

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.logging
    def test_logging_fields_label_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies logging field label"""
        logging = Logging(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            logging.log_level.get_input_label,
            'Log level'
            )

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.logging
    def test_logging_default_log_level(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """This test case checks verification of default log level"""
        logging = Logging(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        default_log_level = "INFO"
        self.assert_util(
            logging.log_level.get_value().lower() ,
            default_log_level.lower()
            )
        
    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.logging
    def test_logging_select_random_log_level(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """This test cases checks the functionality of selecting random log level and verification of the same in UI"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        logging = Logging(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        level = random.choice(levels)
        logging.log_level.select(level)
        logging.save()
        self.assert_util(
            logging.log_level.get_value().lower() ,
            level.lower()
            )
        
    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.logging
    def test_logging_list_log_levels(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """This test case checks list of log levels present in the drop down"""
        logging = Logging(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            logging.log_level.list_of_values(),
            ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            )
        
    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.logging
    @pytest.mark.sanity_test
    def test_logging_selected_log_level_frontend(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """This test case checks the verification of selected log level"""
        selection_log = "WARNING"
        logging = Logging(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        logging.log_level.select(selection_log)
        logging.save()
        self.assert_util(
            logging.log_level.get_value().lower() ,
            selection_log.lower()
            )
        
    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.logging
    @pytest.mark.sanity_test
    def test_logging_selected_log_level_backend(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """This test case checks the verification of selected log level in backend"""
        selection_log = "DEBUG"
        logging = Logging(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        logging.log_level.select(selection_log)
        logging.save()
        log_level = logging.backend_conf.get_parameter("loglevel")
        self.assert_util(
            log_level ,
            selection_log
            )
