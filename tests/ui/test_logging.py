from ucc_smartx.base_test import UccTester
from ucc_smartx.pages.logging import Logging
import pytest
import time
import re
import random
import os

# @pytest.fixture(autouse=True)
# def remove_configuration(ucc_smartx_configs):
#     logging = Logging(ucc_smartx_configs)
#     logging.backend_conf.delete_stanza()


class TestLogging(UccTester):

    @pytest.mark.logging
    #This test case checks verification of default log level
    def test_logging_default_log_level(self, ucc_smartx_configs):
        logging = Logging(ucc_smartx_configs)
        default_log_level = "INFO"
        assert logging.log_level.get_value().lower() == default_log_level.lower()
        
    @pytest.mark.logging
    #This test cases checks the functionality of selecting random log level and verification of the same in UI
    def test_logging_random(self, ucc_smartx_configs):
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        logging = Logging(ucc_smartx_configs)
        level = random.choice(levels)
        logging.log_level.select(level)
        logging.save()
        assert logging.log_level.get_value().lower() == level.lower()
        
    @pytest.mark.logging
    #This test case checks list of log levels present in the drop down
    def test_logging_list(self, ucc_smartx_configs):
        logging = Logging(ucc_smartx_configs)
        assert set(logging.log_level.list_of_values()) == {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        
    @pytest.mark.logging
    #This test case checks the verification of selected log level
    def test_logging_selected_log_level_frontend(self, ucc_smartx_configs):
        selection_log = "WARNING"
        logging = Logging(ucc_smartx_configs)
        logging.log_level.select(selection_log)
        logging.save()
        assert logging.log_level.get_value().lower() == selection_log.lower()
        
    @pytest.mark.logging
    #This test case checks the verification of selected log level in backend
    def test_logging_selected_log_level_backend(self, ucc_smartx_configs):
        selection_log = "DEBUG"
        logging = Logging(ucc_smartx_configs)
        logging.log_level.select(selection_log)
        logging.save()
        # log_level = logging.backend_conf.get_parameter("log_level") in ["WARNING", "ERROR", "DEBUG"]
        log_level = logging.backend_conf.get_parameter("loglevel")
        assert log_level == selection_log
