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

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.account
    def test_account_sort_functionality(
        self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_multiple_account
    ):
        """Verifies sorting functionality for name column"""
        account = AccountPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        account.table.sort_column("Name")
        sort_order = account.table.get_sort_order()
        column_values = list(account.table.get_column_values("Name"))
        column_values = list(str(item) for item in column_values)
        sorted_values = sorted(column_values, key=str.lower)
        self.assert_util(sort_order["header"].lower(), "name")
        self.assert_util(column_values, sorted_values)
        self.assert_util(sort_order["ascending"], True)

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.account
    def test_account_count(
        self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_multiple_account
    ):
        """Verifies count on table"""
        account = AccountPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            account.table.get_count_title,
            "{} Items".format(len(account.backend_conf.get_all_stanzas())),
        )

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.account
    def test_accounts_filter_functionality_negative(
        self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_account
    ):
        """Verifies the filter functionality (Negative)"""
        account = AccountPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        account.table.set_filter("hello")
        self.assert_util(account.table.get_row_count, 0)
        self.assert_util(
            account.table.get_count_title,
            "{} Item".format(account.table.get_row_count()),
        )
        account.table.clean_filter()

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.account
    def test_accounts_filter_functionality_positive(
        self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_account
    ):
        """Verifies the filter functionality (Positive)"""
        account = AccountPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        account.table.set_filter("TestAccount")
        self.assert_util(account.table.get_row_count, 1)
        self.assert_util(
            account.table.get_count_title,
            "{} Item".format(account.table.get_row_count()),
        )
        account.table.clean_filter()

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.account
    def test_account_pagination(
        self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_multiple_account
    ):
        """Verifies pagination list"""
        account = AccountPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        name_column_page1 = account.table.get_column_values("name")
        account.table.switch_to_next()
        name_column_page2 = account.table.get_column_values("name")
        self.assert_util(name_column_page1, name_column_page2, "!=")

    ###################################
    #### TEST CASES FOR ENTITY     ####
    ###################################

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.forwarder
    @pytest.mark.account
    def test_account_title_and_description(
        self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper
    ):
        """Verifies the title and description of the page"""
        account = AccountPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(account.title.wait_to_display, "Configuration")
        self.assert_util(account.description.wait_to_display, "Set up your add-on")
