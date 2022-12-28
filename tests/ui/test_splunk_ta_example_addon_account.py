#
# SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
# SPDX-License-Identifier: LicenseRef-Splunk-8-2021
#
#
from pytest_splunk_addon_ui_smartx.base_test import UccTester
from pytest_splunk_addon_ui_smartx.backend_confs import BackendConf
from .Example_UccLib.account import AccountPage
from .Example_UccLib.input_page import InputPage

import random
import pytest
import re
import time
import configparser
import os
import requests
import urllib
import copy
from base64 import b64decode


ACCOUNT_CONFIG = {
    "name": "TestAccount",
    "account_checkbox": 1,
    "account_multiple_select": "one",
    "account_radio": "yes",
    "auth_type": "basic",
    "custom_endpoint": "login.example.com",
    "username": "TestUser",
    "password": "TestPassword",
    "token": "TestToken",
    "client_id": "",
    "client_secret": "",
    "redirect_url": "",
    "endpoint": "",
    "example_help_link": "",
}


@pytest.fixture
def add_input(ucc_smartx_rest_helper):
    input_page = InputPage(
        ucc_smartx_rest_helper=ucc_smartx_rest_helper, open_page=False
    )
    url = input_page._get_input_endpoint()
    kwargs = {
        "name": "example_input_one://dummy_input_one",
        "account": "TestAccount",
        "input_one_checkbox": "1",
        "input_one_radio": "1",
        "interval": "90",
        "limit": "1000",
        "multipleSelectTest": "a|b",
        "object": "test_object",
        "object_fields": "test_field",
        "order_by": "LastModifiedDate",
        "singleSelectTest": "two",
        "start_date": "2020-12-11T20:00:32.000z",
        "disabled": 0,
    }
    yield input_page.backend_conf.post_stanza(url, kwargs)
    input_page.backend_conf.delete_all_stanzas("search=dummy_input_one")


@pytest.fixture
def add_account(ucc_smartx_rest_helper):
    account = AccountPage(
        ucc_smartx_rest_helper=ucc_smartx_rest_helper, open_page=False
    )
    url = account._get_account_endpoint()
    kwargs = ACCOUNT_CONFIG
    yield account.backend_conf.post_stanza(url, kwargs)


@pytest.fixture
def add_multiple_account(ucc_smartx_rest_helper):
    account = AccountPage(
        ucc_smartx_rest_helper=ucc_smartx_rest_helper, open_page=False
    )
    url = account._get_account_endpoint()
    for i in range(12):
        kwargs = copy.deepcopy(ACCOUNT_CONFIG)
        kwargs["name"] = kwargs["name"] + str(i)
        account.backend_conf.post_stanza(url, kwargs)


@pytest.fixture(autouse=True)
def delete_accounts(ucc_smartx_rest_helper):
    yield
    account = AccountPage(
        ucc_smartx_rest_helper=ucc_smartx_rest_helper, open_page=False
    )
    account.backend_conf.delete_all_stanzas()


class TestAccount(UccTester):

    ############################
    ### TEST CASES FOR TABLE ###
    ############################

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.account
    def test_account_default_rows_in_table(
        self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper
    ):
        """Verifies the default number of rows in the table"""
        account = AccountPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(account.table.get_row_count, 0)
