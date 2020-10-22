from pytest_splunk_addon_ui_smartx.base_test import UccTester
from pytest_splunk_addon_ui_smartx.pages.logging import Logging
from .Example_UccLib.account import AccountPage
from .Example_UccLib.input_page import InputPage
import pytest
import random
import re
import time
from datetime import datetime, timedelta
import configparser
import os
import json
import copy
from base64 import b64decode 


@pytest.fixture(scope="session", autouse=True)
def add_account(ucc_smartx_rest_helper):
    account = AccountPage(ucc_smartx_rest_helper=ucc_smartx_rest_helper, open_page=False)
    url = account._get_account_endpoint()
    kwargs = {
        'name': 'test_input',
        'account_checkbox': 1,
        'account_multiple_select': 'one',
        'account_radio': 'yes',
        'auth_type': 'basic',
        'custom_endpoint': 'login.example.com',
        'username': 'TestUser',
        'password': b64decode(os.getenv("password")).decode("ascii"),
        'token': b64decode(os.getenv("token")).decode("ascii"),
        'client_id': '',
        'client_secret': '',
        'redirect_url': '',
        'endpoint': '',
        'oauth_state_enabled': '',
        'example_help_link': ''
    }
    yield account.backend_conf.post_stanza(url, kwargs)
    account.backend_conf.delete_all_stanzas()

@pytest.fixture
def add_multiple_inputs(ucc_smartx_rest_helper):
    input_page = InputPage(ucc_smartx_rest_helper=ucc_smartx_rest_helper, open_page=False)
    url = input_page._get_input_endpoint()
    for i in range(50):
        kwargs = {
            'name': 'example_input_one://dummy_input_one' + str(i),
            'account':'test_input',
            'input_one_checkbox': '1',
            'input_one_radio': 'yes',
            'interval': '90',
            'limit': '1000',
            'multipleSelectTest': 'a|b',
            'object': 'test_object',
            'object_fields': 'test_field',
            'order_by': 'LastModifiedDate',
            'singleSelectTest': 'two',
            'start_date': '2020-12-11T20:00:32.000z',
            'disabled': 0,
        }
        input_page.backend_conf.post_stanza(url, kwargs)
        kwargs = {
            'name': 'example_input_two://dummy_input_two' + str(i),
            'account':'test_input',
            'input_two_checkbox': '1',
            'input_two_radio': 'no',
            'interval': '100',
            'input_two_multiple_select': 'one,two',
            'index': 'main',
            'start_date': '2016-10-10T12:10:15.000z',
            'disabled': 0,
        }
        input_page.backend_conf.post_stanza(url, kwargs)

@pytest.fixture
def add_input_one(ucc_smartx_rest_helper):
    input_page = InputPage(ucc_smartx_rest_helper=ucc_smartx_rest_helper, open_page=False)
    url = input_page._get_input_endpoint()
    kwargs = {
        'name': 'example_input_one://dummy_input_one',
        'account':'test_input',
        'input_one_checkbox': '1',
        'input_one_radio': 'yes',
        'interval': '90',
        'limit': '1000',
        'multipleSelectTest': 'a|b',
        'object': 'test_object',
        'object_fields': 'test_field',
        'order_by': 'LastModifiedDate',
        'singleSelectTest': 'two',
        'start_date': '2020-12-11T20:00:32.000z',
        'disabled': 0,
    }
    yield input_page.backend_conf.post_stanza(url, kwargs)

@pytest.fixture
def add_input_two(ucc_smartx_rest_helper):
    input_page = InputPage(ucc_smartx_rest_helper = ucc_smartx_rest_helper, open_page=False)
    url = input_page._get_input_endpoint()
    kwargs = {
        'name': 'example_input_two://dummy_input_two',
        'account':'test_input',
        'input_two_checkbox': '1',
        'input_two_radio': 'no',
        'interval': '100',
        'input_two_multiple_select': 'one,two',
        'index': 'main',
        'start_date': '2016-10-10T12:10:15.000z',
        'disabled': 0,
    }
    yield input_page.backend_conf.post_stanza(url, kwargs)

@pytest.fixture(autouse=True)
def delete_inputs(ucc_smartx_rest_helper):
    yield
    input_page = InputPage(ucc_smartx_rest_helper=ucc_smartx_rest_helper, open_page=False)
    input_page.backend_conf.delete_all_stanzas("search=example_input")
    

class TestInput(UccTester):

    ############################
    ### TEST CASES FOR TABLE ###
    ############################


    @pytest.mark.input
    def test_inputs_displayed_columns(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies headers of input table"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        header_list = ["", "Name", "Account", "Interval", "Index", "Status", "Actions"]
        self.assert_util(
            input_page.table.get_headers,
            header_list
            )

    @pytest.mark.input
    def test_inputs_pagination_list(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies pagination list"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            input_page.pagination.get_pagination_list,
            ['10 Per Page','25 Per Page','50 Per Page']
            )

    @pytest.mark.input
    def test_inputs_pagination(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_multiple_inputs):
        """ Verifies pagination functionality by creating 100 accounts"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.open()
        self.assert_util(input_page.pagination.select_page_option, True,left_args={'value':"50 Per Page"})
        self.assert_util(input_page.table.switch_to_page, True,left_args={'value': 2})
        self.assert_util(input_page.table.switch_to_prev, True)
        self.assert_util(input_page.table.switch_to_next, True)

    @pytest.mark.input
    def test_inputs_sort_functionality(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one, add_input_two):
        """ Verifies sorting functionality for name column"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.pagination.select_page_option("50 Per Page")
        input_page.table.sort_column("Name")
        sort_order = input_page.table.get_sort_order()
        column_values = list(input_page.table.get_column_values("Name"))
        column_values = list(str(item)for item in column_values)
        sorted_values = sorted(column_values , key = str.lower)
        self.assert_util(
            sort_order["header"].lower(),
            "name"
            )
        self.assert_util(
            column_values,
            sorted_values
            )
        self.assert_util(sort_order["ascending"], True)

    @pytest.mark.input
    def test_inputs_filter_functionality_negative(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one, add_input_two):
        """ Verifies the filter functionality (Negative)"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.set_filter("hello")
        self.assert_util(input_page.table.get_row_count, 0)
        self.assert_util(
            input_page.table.get_count_title,
            "{} Inputs".format(input_page.table.get_row_count())
            )
        input_page.table.clean_filter()

    @pytest.mark.input
    def test_inputs_filter_functionality_positive(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one, add_input_two):
        """ Verifies the filter functionality (Positive)"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.set_filter("dummy")
        self.assert_util(input_page.table.get_row_count, 2)
        self.assert_util(
            input_page.table.get_count_title,
            "{} Inputs".format(input_page.table.get_row_count())
            )
        input_page.table.clean_filter()

    @pytest.mark.input
    def test_inputs_default_rows_in_table(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the default number of rows in the table"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            input_page.table.get_row_count,
            0
            )

    @pytest.mark.input
    def test_inputs_create_new_input_list_values(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies input list dropdown"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        create_new_input_list = ["Example Input One", "Example Input Two"]
        self.assert_util(
            input_page.create_new_input.get_inputs_list,
            create_new_input_list
            )

    @pytest.mark.input
    def test_inputs_input_type_list_values(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one, add_input_two):
        """ Verifies input type filter list"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        type_filter_list = ["All", "Example Input One", "Example Input Two"]
        self.assert_util(
            input_page.type_filter.get_input_type_list,
            type_filter_list
            )
        input_page.type_filter.select_input_type("Example Input One", open_dropdown=False)
        self.assert_util(
            input_page.table.get_row_count,
            1
            )
        input_page.type_filter.select_input_type("Example Input Two")
        self.assert_util(
            input_page.table.get_row_count,
            1
            )

    @pytest.mark.input
    def test_inputs_delete_enabled_input(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies enabled input should not delete"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            input_page.table.delete_row,
            r"Can't delete enabled input",
            left_args={'name': "dummy_input_one"}
            )

    @pytest.mark.input
    def test_inputs_more_info(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the expand functionality of the inputs table"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            input_page.table.get_more_info,
            {
                'Name': 'dummy_input_one', 
                'Interval': '90',
                'Index': 'default',
                'Status': 'Enabled',
                'Example Account': 'test_input',
                'Object': 'test_object',
                'Object Fields': 'test_field',
                'Order By': 'LastModifiedDate',
                'Query Start Date': '2020-12-11T20:00:32.000z',
                'Limit': '1000'
                },
            left_args={'name': 'dummy_input_one'}
            )

    @pytest.mark.input
    def test_inputs_enable_disable(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the enable and disable functionality of the input"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(input_page.table.input_status_toggle, True, left_args={"name":"dummy_input_one", "enable":False})
        self.assert_util(input_page.table.input_status_toggle, True, left_args={"name":"dummy_input_one", "enable":True})


    @pytest.mark.input
    def test_inputs_count(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one, add_input_two):
        """ Verifies count on table"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            input_page.table.get_count_title,
            "{} Inputs".format(input_page.table.get_row_count())
            )


    @pytest.mark.input
    def test_inputs_title_and_description(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the title and description of the page"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            input_page.title.wait_to_display,
            "Inputs"
            )
        self.assert_util(
            input_page.description.wait_to_display,
            "Manage your data inputs"
            )

    ##########################################
    #### TEST CASES FOR EXAMPLE INPUT ONE ####
    ##########################################

    @pytest.mark.input
    def test_example_input_one_required_field_name(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field name in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.example_radio.select("Yes")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")        
        self.assert_util(
            input_page.entity1.save,
            r"Field Name is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_valid_length_name(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the name field should not be more than 100 characters"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        name_value = "a"* 101
        input_page.entity1.name.set_value(name_value)
        self.assert_util(
            input_page.entity1.save,
            r"Length of input name should be between 1 and 100",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_valid_input_name(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether adding special characters, name field displays validation error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("$$test_name")
        self.assert_util(
            input_page.entity1.save,
            r"Input Name must begin with a letter and consist exclusively of alphanumeric characters and underscores.",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_list_single_select_group_test(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies values Single Select Group Test dropdown in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        single_select_group_test_list = ["One", "Two", "Three", "Four"]
        input_page.create_new_input.select("Example Input One")
        self.assert_util(
            input_page.entity1.single_select_group_test.list_of_values(),
            single_select_group_test_list
            )

    @pytest.mark.input
    def test_example_input_one_select_value_single_select_group_test(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies selected value of Single Select Group Test dropdown in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        selected_value = "Two"
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.single_select_group_test.select(selected_value)
        self.assert_util(
            input_page.entity1.single_select_group_test.get_value,
            selected_value
            )

    @pytest.mark.input
    def test_example_input_one_search_value_single_select_group_test(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies singleselect seach funtionality properly"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        self.assert_util(
            input_page.entity1.single_select_group_test.search_get_list,
            ["One"],
            left_args={'value': 'One'}
            )

    @pytest.mark.input
    def test_example_input_one_default_value_multiple_select_test(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies default values of Multiple Select Test dropdown in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        default_values = ["A", "B"]
        self.assert_util(
            input_page.entity1.multiple_select_test.get_values,
            default_values
            )

    @pytest.mark.input
    def test_example_input_one_list_multiple_select_test(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies values of Multiple Select Test dropdown in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        multiple_select_test = ["A", "B"]
        self.assert_util(
            input_page.entity1.multiple_select_test.list_of_values(),
            multiple_select_test
            )

    @pytest.mark.input
    def test_example_input_one_select_value_multiple_select_test(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies selected single value of Multiple Select Test dropdown in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        selected_value = ["A"]
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        for each in selected_value:
            input_page.entity1.multiple_select_test.select(each)
        self.assert_util(
            input_page.entity1.multiple_select_test.get_values,
            selected_value
            )

    @pytest.mark.input
    def test_example_input_one_select_multiple_values_multiple_select_test(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies selected multiple values of Multiple Select Test dropdown in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        selected_values = ["A", "B"]
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        for each in selected_values:
            input_page.entity1.multiple_select_test.select(each)
        self.assert_util(
            input_page.entity1.multiple_select_test.get_values,
            selected_values
            )

    @pytest.mark.input
    def test_example_input_one_deselect_multiple_select_test(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies deselect in Multiple Select Test dropdown in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        selected_values = ["A", "B"]
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        for each in selected_values:
            input_page.entity1.multiple_select_test.select(each)
        input_page.entity1.multiple_select_test.deselect("A")
        self.assert_util(
            input_page.entity1.multiple_select_test.get_values,
            ["B"]
            )

    @pytest.mark.input
    def test_example_input_one_search_value_multiple_select_test(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies multiple select seach funtionality properly"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        self.assert_util(
            input_page.entity1.multiple_select_test.search_get_list,
            ["A"],
            left_args={'value': 'A'}
            )

    @pytest.mark.input
    def test_example_input_one_default_value_example_checkbox(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies default value of example checkbox in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        self.assert_util(input_page.entity1.example_checkbox.is_checked, True)

    @pytest.mark.input
    def test_example_input_one_unchecked_example_checkbox(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies Uncheck in example checkbox in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        self.assert_util(input_page.entity1.example_checkbox.uncheck, True)

    @pytest.mark.input
    def test_example_input_one_checked_example_checkbox(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies checked in example checkbox in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.example_checkbox.uncheck()
        self.assert_util(input_page.entity1.example_checkbox.check, True)

    @pytest.mark.input
    def test_example_input_one_default_value_example_radio(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies default value of example radio in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        self.assert_util(
            input_page.entity1.example_radio.get_value,
            "Yes"
            )

    @pytest.mark.input
    def test_example_input_one_select_value_example_radio(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies selected value of example radio in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.example_radio.select("No")
        self.assert_util(
            input_page.entity1.example_radio.get_value,
            "No"
            )

    @pytest.mark.input
    def test_example_input_one_required_field_interval(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field interval in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("Yes")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(
            input_page.entity1.save,
            r"Field Interval is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_valid_input_interval(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether adding non numeric values, intreval field displays validation error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        input_page.entity1.interval.set_value("abc")
        self.assert_util(
            input_page.entity1.save,
            r"Interval must be an integer.",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_required_field_index(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field index in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("Yes")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        input_page.entity1.index.cancel_selected_value()
        self.assert_util(
            input_page.entity1.save,
            r"Field Index is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_default_value_index(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies default value of field index in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        default_index = "default"
        input_page.create_new_input.select("Example Input One")
        self.assert_util(
            input_page.entity1.index.get_value,
            default_index
            )

    @pytest.mark.input
    def test_example_input_one_required_field_example_account(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field Salesforce Account in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("Yes")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(
            input_page.entity1.save,
            r"Field Example Account is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_required_field_object(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field Object in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("Yes")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(
            input_page.entity1.save,
            r"Field Object is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_required_field_object_fields(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field Object Fields in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("Yes")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(
            input_page.entity1.save,
            r"Field Object Fields is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_required_field_order_by(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field Order By in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("Yes")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        input_page.entity1.order_by.clear_text()
        self.assert_util(
            input_page.entity1.save,
            r"Field Order By is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_default_value_order_by(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies default value of field Order By in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        default_order_by = "LastModifiedDate"
        input_page.create_new_input.select("Example Input One")
        self.assert_util(
            input_page.entity1.order_by.get_value,
            default_order_by
            )

    @pytest.mark.input
    def test_example_input_one_help_text_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies help text for the field name"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        self.assert_util(
            input_page.entity1.name.get_help_text,
            'A unique name for the data input.'
            )
        self.assert_util(
            input_page.entity1.example_checkbox.get_help_text,
            'This is an example checkbox for the input one entity'
            )
        self.assert_util(
            input_page.entity1.example_radio.get_help_text,
            'This is an example radio button for the input one entity'
            )
        self.assert_util(
            input_page.entity1.interval.get_help_text,
            'Time interval of the data input, in seconds.'
            )
        self.assert_util(
            input_page.entity1.object.get_help_text,
            'The name of the object to query for.'
            )
        self.assert_util(
            input_page.entity1.object_fields.get_help_text,
            'Object fields from which to collect data. Delimit multiple fields using a comma.'
            )
        self.assert_util(
            input_page.entity1.query_start_date.get_help_text,
            'The datetime after which to query and index records, in this format: "YYYY-MM-DDThh:mm:ss.000z". Defaults to 90 days earlier from now.'
            )
        self.assert_util(
            input_page.entity1.limit.get_help_text,
            'The maximum number of results returned by the query.'
            )
        self.assert_util(
            input_page.entity1.order_by.get_help_text,
            'The datetime field by which to query results in ascending order for indexing.'
            )

    @pytest.mark.input
    def test_example_input_one_valid_input_query_start_date(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether adding wrong format, Query Start Date field displays validation error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        input_page.entity1.interval.set_value("120")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_object_field")
        input_page.entity1.query_start_date.set_value("2020/01/01")
        self.assert_util(
            input_page.entity1.save,
            r"Invalid date and time format",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_default_value_limit(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies default value of field limit in example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        default_limit = "1000"
        input_page.create_new_input.select("Example Input One")
        self.assert_util(
            input_page.entity1.limit.get_value,
            default_limit
            )

    @pytest.mark.input
    def test_example_input_one_help_link(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether the help link redirects to the correct URL"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        go_to_link = "https://docs.splunk.com/Documentation"
        input_page.create_new_input.select("Example Input One")
        self.assert_util(
            input_page.entity1.help_link.go_to_link,
            go_to_link
            )


    ###################################
    #### TEST CASES FOR ENTITY ONE ####
    ###################################

    @pytest.mark.input
    def test_example_input_one_add_frontend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the frontend after adding a Example Input One"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("Yes")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(input_page.entity1.save, True)
        input_page.table.wait_for_rows_to_appear(1)
        self.assert_util(
            input_page.table.get_table()["Test_Add"] ,
            {
                'name': 'Test_Add', 
                'account': 'test_input',
                'interval': '90',
                'index': 'default',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }
            )

        url = input_page._get_input_endpoint()

    @pytest.mark.input
    def test_example_input_one_add_backend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the backend after adding a example input one"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("No")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(input_page.entity1.save, True)
        input_page.table.wait_for_rows_to_appear(1)
        value_to_test = {
            'account': 'test_input',
            'input_one_checkbox': '1',
            'input_one_radio': '0',
            'interval': '90',
            'limit': '1000',
            'multipleSelectTest': 'a|b',
            'object': 'test_object',
            'object_fields': 'test_field',
            'order_by': 'LastModifiedDate',
            'singleSelectTest': 'two',
            'start_date': '2020-12-11T20:00:32.000z',
            'disabled': 0,
            }
        backend_stanza = input_page.backend_conf.get_stanza("example_input_one://Test_Add")
        for each_key, each_value in value_to_test.items():
            assert each_key in backend_stanza
            self.assert_util(
                each_value ,
                backend_stanza[each_key],  
                )
                

    @pytest.mark.input
    def test_example_input_one_edit_uneditable_field_name(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the frontend uneditable fields at time of edit of the example input one entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_one")
        self.assert_util(input_page.entity1.name.is_editable, False)

    @pytest.mark.input
    def test_example_input_one_edit_frontend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the frontend edit functionality of the example input one entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_one")
        input_page.entity1.example_checkbox.uncheck()
        input_page.entity1.example_radio.select("No")
        input_page.entity1.single_select_group_test.select("Four")
        input_page.entity1.multiple_select_test.deselect("b")
        input_page.entity1.interval.set_value("3600")
        input_page.entity1.index.select("main")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("edit_object")
        input_page.entity1.object_fields.set_value("edit_field")
        input_page.entity1.order_by.set_value("LastDate")
        input_page.entity1.limit.set_value("2000")
        input_page.entity1.query_start_date.set_value("2020-20-20T20:20:20.000z")
        self.assert_util(input_page.entity1.save, True)
        input_page.table.wait_for_rows_to_appear(1)
        self.assert_util(
            input_page.table.get_table()["dummy_input_one"] ,
            {
                'name': "dummy_input_one", 
                'account': 'test_input',
                'interval': '3600',
                'index': 'main',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete'
            }
            )

    @pytest.mark.input
    def test_example_input_one_edit_backend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the backend edit functionality of the example input one entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_one")
        input_page.entity1.example_checkbox.uncheck()
        input_page.entity1.example_radio.select("No")
        input_page.entity1.single_select_group_test.select("Four")
        input_page.entity1.multiple_select_test.deselect("b")
        input_page.entity1.interval.set_value("3600")
        input_page.entity1.index.select("main")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("edit_object")
        input_page.entity1.object_fields.set_value("edit_field")
        input_page.entity1.order_by.set_value("LastDate")
        input_page.entity1.limit.set_value("2000")
        input_page.entity1.query_start_date.set_value("2020-20-20T20:20:20.000z")
        self.assert_util(input_page.entity1.save, True)
        input_page.table.wait_for_rows_to_appear(1)
        value_to_test = {
            'account': 'test_input',
            'input_one_checkbox': '0',
            'input_one_radio': '0',
            'interval': '3600',
            'index': 'main',
            'limit': '2000',
            'multipleSelectTest': 'a',
            'object': 'edit_object',
            'object_fields': 'edit_field',
            'order_by': 'LastDate',
            'singleSelectTest': 'four',
            'start_date': '2020-20-20T20:20:20.000z',
            'disabled': 0,
            }
        backend_stanza = input_page.backend_conf.get_stanza("example_input_one://dummy_input_one")
        for each_key, each_value in value_to_test.items():
            self.assert_util(
                each_value,
                backend_stanza[each_key]
                )

    @pytest.mark.input
    def test_example_input_one_clone_default_values(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the frontend default fields at time of clone for example input one entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_one")
        self.assert_util(
            input_page.entity1.name.get_value,
            ""
            )
        self.assert_util(input_page.entity1.example_checkbox.is_checked, True)
        self.assert_util(
            input_page.entity1.example_radio.get_value,
            "Yes"
            )
        self.assert_util(
            input_page.entity1.single_select_group_test.get_value,
            "Two"
            )
        self.assert_util(
            input_page.entity1.multiple_select_test.get_values,
            ["A", "B"]
            )
        self.assert_util(
            input_page.entity1.interval.get_value,
            "90"
            )
        self.assert_util(
            input_page.entity1.index.get_value,
            "default"
            )
        self.assert_util(
            input_page.entity1.example_account.get_value,
            "test_input"
            )
        self.assert_util(
            input_page.entity1.object.get_value,
            "test_object"
            )
        self.assert_util(
            input_page.entity1.object_fields.get_value,
            "test_field"
            )
        self.assert_util(
            input_page.entity1.order_by.get_value,
            "LastModifiedDate"
            )
        self.assert_util(
            input_page.entity1.query_start_date.get_value,
            "2020-12-11T20:00:32.000z"
            )
        self.assert_util(
            input_page.entity1.limit.get_value,
            "1000"
            )

    @pytest.mark.input
    def test_example_input_one_clone_frontend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the frontend clone functionality of the example input one entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.wait_for_rows_to_appear(1)
        input_page.table.clone_row("dummy_input_one")
        input_page.entity1.name.set_value("Clone_Test")
        input_page.entity1.interval.set_value("180")
        input_page.entity1.limit.set_value("500")
        self.assert_util(input_page.entity1.save, True)
        input_page.table.wait_for_rows_to_appear(2)
        self.assert_util(
            input_page.table.get_table()["Clone_Test"] ,
            {
                'name': 'Clone_Test', 
                'account': 'test_input',
                'interval': '180',
                'index': 'default',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }
            )

    @pytest.mark.input
    def test_example_input_one_clone_backend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the backend clone functionality of the example input one entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.wait_for_rows_to_appear(1)
        input_page.table.clone_row("dummy_input_one")
        input_page.entity1.name.set_value("Clone_Test")
        input_page.entity1.interval.set_value("180")
        input_page.entity1.limit.set_value("500")
        self.assert_util(input_page.entity1.save, True)
        input_page.table.wait_for_rows_to_appear(2)
        value_to_test = {
            'account': 'test_input',
            'input_one_checkbox': '1',
            'input_one_radio': '1',
            'interval': '180',
            'index': 'default',
            'limit': '500',
            'multipleSelectTest': 'a|b',
            'object': 'test_object',
            'object_fields': 'test_field',
            'order_by': 'LastModifiedDate',
            'singleSelectTest': 'two',
            'start_date': '2020-12-11T20:00:32.000z',
            'disabled': 0,
            }
        backend_stanza = input_page.backend_conf.get_stanza("example_input_one://Clone_Test")
        for each_key, each_value in value_to_test.items():
            self.assert_util(
                each_value ,
                backend_stanza[each_key]
                )

    @pytest.mark.input
    def test_example_input_one_delete_row_frontend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the frontend delete functionlity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.input_status_toggle("dummy_input_one", enable=False)
        input_page.table.delete_row("dummy_input_one")
        input_page.table.wait_for_rows_to_appear(0)
        self.assert_util(
            "dummy_input_one",
            input_page.table.get_table,
            "not in"
            )

    @pytest.mark.input
    def test_example_input_one_delete_row_backend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the backend delete functionlity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.input_status_toggle("dummy_input_one", enable=False)
        input_page.table.delete_row("dummy_input_one")
        input_page.table.wait_for_rows_to_appear(0)
        self.assert_util(
            "example_input_one://dummy_input_one",
            input_page.backend_conf.get_all_stanzas().keys(),
            "not in"
            )

    @pytest.mark.input
    def test_example_input_one_add_close_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies close functionality at time of add"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        self.assert_util(input_page.entity1.close, True)

    @pytest.mark.input
    def test_example_input_one_edit_close_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies close functionality at time of edit"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_one")
        self.assert_util(input_page.entity1.close, True)

    @pytest.mark.input
    def test_example_input_one_clone_close_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies close functionality at time of clone"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_one")
        self.assert_util(input_page.entity1.close, True)

    @pytest.mark.input
    def test_example_input_one_delete_close_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies close functionality at time of delete"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(input_page.table.delete_row, True, left_args={"name":"dummy_input_one", "close":True})

    @pytest.mark.input
    def test_example_input_one_add_cancel_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies cancel functionality at time of add"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        self.assert_util(input_page.entity1.cancel, True)

    @pytest.mark.input
    def test_example_input_one_edit_cancel_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies cancel functionality at time of edit"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_one")
        self.assert_util(input_page.entity1.cancel, True)

    @pytest.mark.input
    def test_example_input_one_clone_cancel_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies cancel functionality at time of clone"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_one")
        self.assert_util(input_page.entity1.cancel, True)

    @pytest.mark.input
    def test_example_input_one_delete_cancel_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies cancel functionality at time of delete"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(input_page.table.delete_row, True, left_args={"name":"dummy_input_one", "cancel":True})

    @pytest.mark.input
    def test_example_input_one_add_duplicate_names(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies by saving an entity with duplicate name it displays and error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        input_name = "dummy_input_one"
        input_page.entity1.name.set_value(input_name)
        self.assert_util(
            input_page.entity1.save,
            "Name {} is already in use".format(input_name),
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_clone_duplicate_names(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies by saving an entity with duplicate name at time of clone it displays and error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_one")
        input_name = "dummy_input_one"
        input_page.entity1.name.set_value(input_name)
        self.assert_util(
            input_page.entity1.save,
            "Name {} is already in use".format(input_name),
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity1.close_error, True)

    @pytest.mark.input
    def test_example_input_one_add_valid_title(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the title of the 'Add Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input One")
        self.assert_util(
            input_page.entity1.title.container.get_attribute('textContent').strip(),
            "Add Example Input One"
            )

    @pytest.mark.input
    def test_example_input_one_edit_valid_title(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the title of the 'Edit Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_one")
        self.assert_util(
            input_page.entity1.title.container.get_attribute('textContent').strip(),
            "Update Example Input One"
            )

    @pytest.mark.input
    def test_example_input_one_clone_valid_title(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the title of the 'Clone Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_one")
        self.assert_util(
            input_page.entity1.title.container.get_attribute('textContent').strip(),
            "Clone Example Input One"
            )

    @pytest.mark.input
    def test_example_input_one_delete_valid_title(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the title of the 'Delete Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.delete_row("dummy_input_one", prompt_msg=True)
        self.assert_util(
            input_page.entity1.title.container.get_attribute('textContent').strip(),
            "Delete Confirmation"
            )

    @pytest.mark.input
    def test_example_input_one_delete_valid_prompt_message(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_one):
        """ Verifies the prompt message of the 'Delete Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_name = "dummy_input_one"
        prompt_message = input_page.table.delete_row("dummy_input_one", prompt_msg=True)
        self.assert_util(
            prompt_message ,
            'Are you sure you want to delete "{}" ?'.format(input_name)
            )
    


    ############################
    ### TEST CASES FOR TABLE ###
    ############################


    ##########################################
    #### TEST CASES FOR EXAMPLE INPUT TWO ####
    ##########################################

    @pytest.mark.input
    def test_example_input_two_required_field_name(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field name in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.example_checkbox.check()
        input_page.entity2.example_radio.select("No")
        input_page.entity2.example_multiple_select.select("Option One")
        input_page.entity2.index.select("main")
        input_page.entity2.interval.set_value("90")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-12-11T20:00:32.000z")        
        self.assert_util(
            input_page.entity2.save,
            r"Field Name is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    @pytest.mark.input
    def test_example_input_two_valid_length_name(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the name field should not be more than 100 characters"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        name_value = "a"* 101
        input_page.entity2.name.set_value(name_value)
        self.assert_util(
            input_page.entity2.save,
            r"Length of input name should be between 1 and 100",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    @pytest.mark.input
    def test_example_input_two_valid_input_name(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether adding special characters, name field displays validation error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("$$test_name_two")
        self.assert_util(
            input_page.entity2.save,
            r"Input Name must begin with a letter and consist exclusively of alphanumeric characters and underscores.",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    @pytest.mark.input
    def test_example_input_two_required_field_interval(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field interval in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("Test_Add")
        input_page.entity2.example_checkbox.check()
        input_page.entity2.example_radio.select("No")
        input_page.entity2.example_multiple_select.select("Option One")
        input_page.entity2.index.select("main")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(
            input_page.entity2.save,
            r"Field Interval is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    @pytest.mark.input
    def test_example_input_two_valid_input_interval(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether adding non numeric values, intreval field displays validation error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("test_name_two")
        input_page.entity2.interval.set_value("abc")
        self.assert_util(
            input_page.entity2.save,
            r"Interval must be an integer.",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    @pytest.mark.input
    def test_example_input_two_required_field_index(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field index in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("Test_Add")
        input_page.entity2.example_checkbox.check()
        input_page.entity2.example_radio.select("No")
        input_page.entity2.example_multiple_select.select("Option One")
        input_page.entity2.interval.set_value("90")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-12-11T20:00:32.000z")
        input_page.entity2.index.cancel_selected_value()
        self.assert_util(
            input_page.entity2.save,
            r"Field Index is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    @pytest.mark.input
    def test_example_input_two_default_value_index(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies default value of field index in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        default_index = "default"
        input_page.create_new_input.select("Example Input Two")
        self.assert_util(
            input_page.entity2.index.get_value,
            default_index
            )

    @pytest.mark.input
    def test_example_input_two_required_field_example_example_account(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field Account in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("Test_Add")
        input_page.entity2.example_checkbox.check()
        input_page.entity2.example_radio.select("No")
        input_page.entity2.example_multiple_select.select("Option One")
        input_page.entity2.index.select("main")
        input_page.entity2.interval.set_value("90")
        input_page.entity2.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(
            input_page.entity2.save,
            r"Field Example Account is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    @pytest.mark.input
    def test_example_input_two_required_field_example_multiple_select(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies required field Example Multiple Select in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("Test_Add")
        input_page.entity2.example_checkbox.check()
        input_page.entity2.example_radio.select("No")
        input_page.entity2.index.select("main")
        input_page.entity2.interval.set_value("90")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(
            input_page.entity2.save,
            r"Field Example Multiple Select is required",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    @pytest.mark.input
    def test_example_input_two_list_example_multiple_select(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies values of Multiple Select Test dropdown in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        example_multiple_select_list = ["Option One", "Option Two"]
        self.assert_util(
            input_page.entity2.example_multiple_select.list_of_values(),
            example_multiple_select_list
            )

    @pytest.mark.input
    def test_example_input_two_select_select_value_example_multiple_select(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies selected single value of Multiple Select Test dropdown in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        selected_value = ["Option One"]
        input_page.create_new_input.select("Example Input Two")
        for each in selected_value:
            input_page.entity2.example_multiple_select.select(each)
        self.assert_util(
            input_page.entity2.example_multiple_select.get_values,
            selected_value
            )

    @pytest.mark.input
    def test_example_input_two_select_multiple_values_example_multiple_select(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies selected multiple values of Multiple Select Test dropdown in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        selected_values = ["Option One", "Option Two"]
        input_page.create_new_input.select("Example Input Two")
        for each in selected_values:
            input_page.entity2.example_multiple_select.select(each)
        self.assert_util(
            input_page.entity2.example_multiple_select.get_values,
            selected_values
            )

    @pytest.mark.input
    def test_example_input_two_help_text_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies help text for the field name"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        self.assert_util(
            input_page.entity2.example_multiple_select.get_help_text,
            'This is an example multipleSelect for input two entity'
            )
        self.assert_util(
            input_page.entity2.name.get_help_text,
            'A unique name for the data input.'
            )
        self.assert_util(
            input_page.entity2.interval.get_help_text,
            'Time interval of the data input, in seconds .'
            )
        self.assert_util(
            input_page.entity2.example_checkbox.get_help_text,
            'This is an example checkbox for the input two entity'
            )
        self.assert_util(
            input_page.entity2.example_radio.get_help_text,
            'This is an example radio button for the input two entity'
            )

    @pytest.mark.input
    def test_example_input_two_checked_example_checkbox(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies Check in example checkbox in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        self.assert_util(input_page.entity2.example_checkbox.check, True)

    @pytest.mark.input
    def test_example_input_two_unchecked_example_checkbox(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies Uncheck in example checkbox in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.example_checkbox.check()
        self.assert_util(input_page.entity2.example_checkbox.uncheck, True)

    @pytest.mark.input
    def test_example_input_two_required_field_example_radio(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies default value of example radio in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("Test_Add")
        input_page.entity2.example_checkbox.check()
        input_page.entity2.example_multiple_select.select("Option One")
        input_page.entity2.index.select("main")
        input_page.entity2.interval.set_value("90")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(
            input_page.entity2.save,
            r"Field Example Radio is required",
            left_args={'expect_error': True}
            )

    @pytest.mark.input
    def test_example_input_two_select_value_example_radio(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies default value of example radio in Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.example_radio.select("No")
        self.assert_util(
            input_page.entity2.example_radio.get_value,
            "No"
            )

    @pytest.mark.input
    def test_example_input_two_valid_input_query_start_date(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether adding wrong format, Query Start Date field displays validation error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("test_name_two")
        input_page.entity2.interval.set_value("120")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.example_multiple_select.select("Option One")
        input_page.entity2.example_radio.select("Yes")
        input_page.entity2.query_start_date.set_value("2020/01/01")
        self.assert_util(
            input_page.entity2.save,
            r"Invalid date and time format",
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    ###################################
    #### TEST CASES FOR ENTITY TWO ####
    ###################################

    @pytest.mark.input
    def test_example_input_two_add_frontend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the frontend after adding a Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("Test_Add")
        input_page.entity2.example_checkbox.check()
        input_page.entity2.example_radio.select("No")
        input_page.entity2.example_multiple_select.select("Option One")
        input_page.entity2.example_multiple_select.select("Option Two")
        input_page.entity2.index.select("main")
        input_page.entity2.interval.set_value("90")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(input_page.entity2.save, True)
        input_page.table.wait_for_rows_to_appear(1)
        self.assert_util(
            input_page.table.get_table()["Test_Add"] ,
            {
                'name': 'Test_Add', 
                'account': 'test_input',
                'interval': '90',
                'index': 'main',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }
            )
        url = input_page._get_input_endpoint()

    @pytest.mark.input
    def test_example_input_two_add_backend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the backend after adding a Example Input Two"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("Test_Add")
        input_page.entity2.example_checkbox.check()
        input_page.entity2.example_radio.select("No")
        input_page.entity2.example_multiple_select.select("Option One")
        input_page.entity2.example_multiple_select.select("Option Two")
        input_page.entity2.index.select("main")
        input_page.entity2.interval.set_value("90")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-12-11T20:00:32.000z")
        self.assert_util(input_page.entity2.save, True)
        input_page.table.wait_for_rows_to_appear(1)
        value_to_test = {
            'account': 'test_input',
            'index': 'main',
            'input_two_checkbox': '1',
            'input_two_radio': '0',
            'interval': '90',
            'input_two_multiple_select': 'one,two',
            'start_date': '2020-12-11T20:00:32.000z',
            'disabled': 0,
            }
        backend_stanza = input_page.backend_conf.get_stanza("example_input_two://Test_Add")
        for each_key, each_value in value_to_test.items():
            self.assert_util(
                each_value ,
                backend_stanza[each_key]
                )

    @pytest.mark.input
    def test_example_input_two_edit_uneditable_field_name(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the frontend uneditable fields at time of edit of the Example Input Two entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_two")
        self.assert_util(input_page.entity2.name.is_editable, False)

    @pytest.mark.input
    def test_example_input_two_edit_frontend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the frontend edit functionality of the Example Input Two entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_two")
        input_page.entity2.example_checkbox.uncheck()
        input_page.entity2.example_radio.select("Yes")
        input_page.entity2.example_multiple_select.deselect("Option One")
        input_page.entity2.interval.set_value("3600")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-20-20T20:20:20.000z")
        self.assert_util(input_page.entity2.save, True)
        input_page.table.wait_for_rows_to_appear(1)
        self.assert_util(
            input_page.table.get_table()["dummy_input_two"] ,
            {
                'name': "dummy_input_two", 
                'account': 'test_input',
                'interval': '3600',
                'index': 'main',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }
            )
    
    @pytest.mark.input
    def test_example_input_two_edit_backend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the backend edit functionality of the Example Input Two entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_two")
        input_page.entity2.example_checkbox.uncheck()
        input_page.entity2.example_radio.select("Yes")
        input_page.entity2.example_multiple_select.deselect("Option One")
        input_page.entity2.interval.set_value("3600")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-20-20T20:20:20.000z")
        self.assert_util(input_page.entity2.save, True)
        input_page.table.wait_for_rows_to_appear(1)
        value_to_test = {
            'account': 'test_input',
            'input_two_checkbox': '0',
            'input_two_radio': '1',
            'interval': '3600',
            'index': 'main',
            'input_two_multiple_select': 'two',
            'start_date': '2020-20-20T20:20:20.000z',
            'disabled': 0,
            }
        backend_stanza = input_page.backend_conf.get_stanza("example_input_two://dummy_input_two")
        for each_key, each_value in value_to_test.items():
            self.assert_util(
                each_value ,
                backend_stanza[each_key]
                )

    @pytest.mark.input
    def test_example_input_two_clone_default_values(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the frontend default fields at time of clone for Example Input Two entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_two")
        self.assert_util(
            input_page.entity2.name.get_value,
            ""
            )
        self.assert_util(input_page.entity2.example_checkbox.is_checked, True)
        self.assert_util(
            input_page.entity2.example_radio.get_value,
            "No"
            )
        self.assert_util(
            input_page.entity2.example_multiple_select.get_values,
            ["Option One", "Option Two"]
            )
        self.assert_util(
            input_page.entity2.interval.get_value,
            "100"
            )
        self.assert_util(
            input_page.entity2.index.get_value,
            "main"
            )
        self.assert_util(
            input_page.entity2.example_account.get_value,
            "test_input"
            )
        self.assert_util(
            input_page.entity2.query_start_date.get_value,
            "2016-10-10T12:10:15.000z"
            )

    @pytest.mark.input
    def test_example_input_two_clone_frontend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the frontend clone functionality of the Example Input Two entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.wait_for_rows_to_appear(1)
        input_page.table.clone_row("dummy_input_two")
        input_page.entity2.name.set_value("Clone_Test")
        input_page.entity2.interval.set_value("180")
        self.assert_util(input_page.entity2.save, True)
        input_page.table.wait_for_rows_to_appear(2)
        self.assert_util(
            input_page.table.get_table()["Clone_Test"] ,
            {
                'name': 'Clone_Test', 
                'account': 'test_input',
                'interval': '180',
                'index': 'main',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }
            )

    @pytest.mark.input
    def test_example_input_two_clone_backend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the backend clone functionality of the Example Input Two entity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.wait_for_rows_to_appear(1)
        input_page.table.clone_row("dummy_input_two")
        input_page.entity2.name.set_value("Clone_Test")
        input_page.entity2.interval.set_value("180")
        self.assert_util(input_page.entity2.save, True)
        input_page.table.wait_for_rows_to_appear(2)
        value_to_test = {
            'account': 'test_input',
            'input_two_checkbox': '1',
            'input_two_radio': '0',
            'interval': '180',
            'index': 'main',
            'input_two_multiple_select': 'one,two',
            'start_date': '2016-10-10T12:10:15.000z',
            'disabled': 0,
            }
        backend_stanza = input_page.backend_conf.get_stanza("example_input_two://Clone_Test")
        for each_key, each_value in value_to_test.items():
            self.assert_util(
                each_value ,
                backend_stanza[each_key]
                    )

    @pytest.mark.input
    def test_example_input_two_delete_row_frontend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the frontend delete functionlity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.input_status_toggle("dummy_input_two", enable=False)
        input_page.table.delete_row("dummy_input_two")
        input_page.table.wait_for_rows_to_appear(0)
        self.assert_util(
                "dummy_input_two",
                input_page.table.get_table,
                "not in"
                )

    @pytest.mark.input
    def test_example_input_two_delete_row_backend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the backend delete functionlity"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.input_status_toggle("dummy_input_two", enable=False)
        input_page.table.delete_row("dummy_input_two")
        input_page.table.wait_for_rows_to_appear(0)
        self.assert_util(
                "example_input_two://dummy_input_two",
                input_page.backend_conf.get_all_stanzas().keys(),
                "not in"
                )

    @pytest.mark.input
    def test_example_input_two_add_close_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies close functionality at time of add"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        self.assert_util(input_page.entity2.close, True)

    @pytest.mark.input
    def test_example_input_two_edit_close_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies close functionality at time of edit"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_two")
        self.assert_util(input_page.entity2.close, True)

    @pytest.mark.input
    def test_example_input_two_clone_close_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies close functionality at time of clone"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_two")
        self.assert_util(input_page.entity2.close, True)

    @pytest.mark.input
    def test_example_input_two_delete_close_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies close functionality at time of delete"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(input_page.table.delete_row, True, left_args={"name":"dummy_input_two", "close":True})

    @pytest.mark.input
    def test_example_input_two_add_cancel_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies cancel functionality at time of add"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        self.assert_util(input_page.entity2.cancel, True)

    @pytest.mark.input
    def test_example_input_two_edit_cancel_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies cancel functionality at time of edit"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_two")
        self.assert_util(input_page.entity2.cancel, True)

    @pytest.mark.input
    def test_example_input_two_clone_cancel_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies cancel functionality at time of clone"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_two")
        self.assert_util(input_page.entity2.cancel, True)

    @pytest.mark.input
    def test_example_input_two_delete_cancel_entity(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies cancel functionality at time of delete"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(input_page.table.delete_row, True, left_args={"name":"dummy_input_two", "cancel":True})

    @pytest.mark.input
    def test_example_input_two_add_duplicate_names(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies by saving an entity with duplicate name it displays and error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        input_name = "dummy_input_two"
        input_page.entity2.name.set_value(input_name)
        self.assert_util(
            input_page.entity2.save,
            "Name {} is already in use".format(input_name),
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)

    @pytest.mark.input
    def test_example_input_two_clone_duplicate_names(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies by saving an entity with duplicate name at time of clone it displays and error"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_two")
        input_name = "dummy_input_two"
        input_page.entity2.name.set_value(input_name)
        self.assert_util(
            input_page.entity2.save,
            "Name {} is already in use".format(input_name),
            left_args={'expect_error': True}
            )
        self.assert_util(input_page.entity2.close_error, True)


    @pytest.mark.input
    def test_example_input_two_add_valid_title(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the title of the 'Add Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.create_new_input.select("Example Input Two")
        self.assert_util(
            input_page.entity2.title.container.get_attribute('textContent').strip(),
            "Add Example Input Two"
            )

    @pytest.mark.input
    def test_example_input_two_edit_valid_title(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the title of the 'Edit Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.edit_row("dummy_input_two")
        self.assert_util(
            input_page.entity2.title.container.get_attribute('textContent').strip(),
            "Update Example Input Two"
            )

    @pytest.mark.input
    def test_example_input_two_clone_valid_title(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the title of the 'Clone Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.clone_row("dummy_input_two")
        self.assert_util(
            input_page.entity2.title.container.get_attribute('textContent').strip(),
            "Clone Example Input Two"
            )

    @pytest.mark.input
    def test_example_input_two_delete_valid_title(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the title of the 'Delete Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_page.table.delete_row("dummy_input_two", prompt_msg=True)
        self.assert_util(
            input_page.entity2.title.container.get_attribute('textContent').strip(),
            "Delete Confirmation"
            )

    @pytest.mark.input
    def test_example_input_two_delete_valid_prompt_message(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper, add_input_two):
        """ Verifies the prompt message of the 'Delete Entity'"""
        input_page = InputPage(ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        input_name = "dummy_input_two"
        prompt_message = input_page.table.delete_row("dummy_input_two", prompt_msg=True)
        self.assert_util(
            prompt_message ,
            'Are you sure you want to delete "{}" ?'.format(input_name)
            )