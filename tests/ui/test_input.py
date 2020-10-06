from ucc_smartx.base_test import UccTester
from ucc_smartx.pages.logging import Logging
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


@pytest.fixture(scope="session", autouse=True)
def add_account(ucc_smartx_configs):
    account = AccountPage(ucc_smartx_configs)
    url = account._get_account_endpoint()
    kwargs = {
        'name': 'test_input',
        'account_checkbox': 1,
        'account_multiple_select': 'one',
        'account_radio': 'yes',
        'auth_type': 'basic',
        'custom_endpoint': 'login.example.com',
        'username': 'TestUser',
        'password': 'TestPassword',
        'token': 'TestToken',
        'disabled': 0,
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
def add_multiple_inputs(ucc_smartx_configs):
    input_page = InputPage(ucc_smartx_configs)
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
def add_input_one(ucc_smartx_configs):
    input_page = InputPage(ucc_smartx_configs)
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
def add_input_two(ucc_smartx_configs):
    input_page = InputPage(ucc_smartx_configs)
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
def delete_inputs(ucc_smartx_configs):
    yield
    input_page = InputPage(ucc_smartx_configs)
    input_page.backend_conf.delete_all_stanzas("search=example_input")
    

class TestInput(UccTester):

    ##########################################
    #### TEST CASES FOR EXAMPLE INPUT ONE ####
    ##########################################

    @pytest.mark.input
    # Verifies required field name in example input one
    def test_example_input_one_required_field_name(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.save(expect_error=True) == r"Field Name is required"
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies the name field should not be more than 100 characters
    def test_example_input_one_valid_length_name(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        name_value = "a"* 101
        input_page.entity1.name.set_value(name_value)
        assert input_page.entity1.save(expect_error=True) == r"Length of input name should be between 1 and 100"
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies whether adding special characters, name field displays validation error
    def test_example_input_one_valid_input_name(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("$$test_name")
        assert input_page.entity1.save(expect_error=True) == r"Input Name must begin with a letter and consist exclusively of alphanumeric characters and underscores."
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies values Single Select Group Test dropdown in example input one
    def test_example_input_one_list_single_select_group_test(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        single_select_group_test_list = ["One", "Two", "Three", "Four"]
        input_page.create_new_input.select("Example Input One")
        assert list(input_page.entity1.single_select_group_test.list_of_values()) == single_select_group_test_list

    @pytest.mark.input
    # Verifies selected value of Single Select Group Test dropdown in example input one
    def test_example_input_one_select_value_single_select_group_test(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        selected_value = "Two"
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.single_select_group_test.select(selected_value)
        assert input_page.entity1.single_select_group_test.get_value() == selected_value

    @pytest.mark.input
    # Verifies singleselect seach funtionality properly
    def test_example_input_one_search_value_single_select_group_test(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One") 
        assert input_page.entity1.single_select_group_test.search_get_list("One") == ["One"]

    @pytest.mark.input
    # Verifies default values of Multiple Select Test dropdown in example input one
    def test_example_input_one_default_value_multiple_select_test(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        default_values = ["A", "B"]
        assert input_page.entity1.multiple_select_test.get_values() == default_values

    @pytest.mark.input
    # Verifies values of Multiple Select Test dropdown in example input one
    def test_example_input_one_list_multiple_select_test(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        multiple_select_test = ["A", "B"]
        assert list(input_page.entity1.multiple_select_test.list_of_values()) == multiple_select_test

    @pytest.mark.input
    # Verifies selected single value of Multiple Select Test dropdown in example input one
    def test_example_input_one_select_value_multiple_select_test(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        selected_value = ["A"]
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        for each in selected_value:
            input_page.entity1.multiple_select_test.select(each)
        assert input_page.entity1.multiple_select_test.get_values() == selected_value

    @pytest.mark.input
    # Verifies selected multiple values of Multiple Select Test dropdown in example input one
    def test_example_input_one_select_multiple_values_multiple_select_test(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        selected_values = ["A", "B"]
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        for each in selected_values:
            input_page.entity1.multiple_select_test.select(each)
        assert input_page.entity1.multiple_select_test.get_values() == selected_values

    @pytest.mark.input
    # Verifies deselect in Multiple Select Test dropdown in example input one
    def test_example_input_one_deselect_multiple_select_test(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        selected_values = ["A", "B"]
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        for each in selected_values:
            input_page.entity1.multiple_select_test.select(each)
        input_page.entity1.multiple_select_test.deselect("A")
        assert input_page.entity1.multiple_select_test.get_values() == ["B"]

    @pytest.mark.input
    # Verifies multiple select seach funtionality properly
    def test_example_input_one_search_value_multiple_select_test(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.multiple_select_test.deselect_all()
        assert input_page.entity1.multiple_select_test.search_get_list("A") == ["A"]

    @pytest.mark.input
    # Verifies default value of example checkbox in example input one
    def test_example_input_one_default_value_example_checkbox(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.example_checkbox.is_checked()

    @pytest.mark.input
    # Verifies Uncheck in example checkbox in example input one
    def test_example_input_one_unchecked_example_checkbox(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.example_checkbox.uncheck()

    @pytest.mark.input
    # Verifies checked in example checkbox in example input one
    def test_example_input_one_checked_example_checkbox(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.example_checkbox.uncheck()
        assert input_page.entity1.example_checkbox.check()

    @pytest.mark.input
    # Verifies default value of example radio in example input one
    def test_example_input_one_default_value_example_radio(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.example_radio.get_value() == "Yes"

    @pytest.mark.input
    # Verifies selected value of example radio in example input one
    def test_example_input_one_select_value_example_radio(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.example_radio.select("No")
        assert input_page.entity1.example_radio.get_value() == "No"

    @pytest.mark.input
    # Verifies required field interval in example input one
    def test_example_input_one_required_field_interval(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        assert input_page.entity1.save(expect_error=True) == r"Field Interval is required"
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies whether adding non numeric values, intreval field displays validation error
    def test_example_input_one_valid_input_interval(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        input_page.entity1.interval.set_value("abc")
        assert input_page.entity1.save(expect_error=True) == r"Interval must be an integer."
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies required field index in example input one
    def test_example_input_one_required_field_index(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        input_page.entity1.interval.set_value("120")
        input_page.entity1.index.cancel_selected_value()
        assert input_page.entity1.save(expect_error=True) == r"Field Index is required"
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies default value of field index in example input one
    def test_example_input_one_default_value_index(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        default_index = "default"
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.index.get_value() == default_index

    @pytest.mark.input
    # Verifies required field Salesforce Account in example input one
    def test_example_input_one_required_field_example_account(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        input_page.entity1.interval.set_value("120")
        assert input_page.entity1.save(expect_error=True) == r"Field Example Account is required"
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies required field Object in example input one
    def test_example_input_one_required_field_object(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        input_page.entity1.interval.set_value("120")
        input_page.entity1.example_account.select("test_input")
        assert input_page.entity1.save(expect_error=True) == r"Field Object is required"
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies required field Object Fields in example input one
    def test_example_input_one_required_field_object_fields(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        input_page.entity1.interval.set_value("120")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        assert input_page.entity1.save(expect_error=True) == r"Field Object Fields is required"
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies required field Order By in example input one
    def test_example_input_one_required_field_order_by(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        input_page.entity1.interval.set_value("120")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_object_field")
        input_page.entity1.order_by.clear_text()
        assert input_page.entity1.save(expect_error=True) == r"Field Order By is required"
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies default value of field Order By in example input one
    def test_example_input_one_default_value_order_by(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        default_order_by = "LastModifiedDate"
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.order_by.get_value() == default_order_by

    @pytest.mark.input
    # Verifies whether adding wrong format, Query Start Date field displays validation error
    def test_example_input_one_valid_input_query_start_date(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("test_name")
        input_page.entity1.interval.set_value("120")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_object_field")
        input_page.entity1.query_start_date.set_value("2020/01/01")
        assert input_page.entity1.save(expect_error=True) == r"Invalid date and time format"
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies default value of field limit in example input one
    def test_example_input_one_default_value_limit(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        default_limit = "1000"
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.limit.get_value() == default_limit

    @pytest.mark.input
    # Verifies whether the help link redirects to the correct URL
    def test_example_input_one_help_link(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        go_to_link = "https://docs.splunk.com/Documentation"
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.help_link.go_to_link() == go_to_link


    ###################################
    #### TEST CASES FOR ENTITY ONE ####
    ###################################

    @pytest.mark.input
    # Verifies the frontend after adding a Example Input One
    def test_example_input_one_add_frontend_validation(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("Yes")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        assert input_page.entity1.save()
        assert input_page.table.get_table()["Test_Add"] == { 
                'name': 'Test_Add', 
                'account': 'test_input',
                'interval': '90',
                'index': 'default',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }
        url = input_page._get_input_endpoint()

    @pytest.mark.input
    # Verifies the backend after adding a example input one
    def test_example_input_one_add_backend_validation(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_page.entity1.name.set_value("Test_Add")
        input_page.entity1.example_radio.select("No")
        input_page.entity1.single_select_group_test.select("Two")
        input_page.entity1.interval.set_value("90")
        input_page.entity1.example_account.select("test_input")
        input_page.entity1.object.set_value("test_object")
        input_page.entity1.object_fields.set_value("test_field")
        input_page.entity1.query_start_date.set_value("2020-12-11T20:00:32.000z")
        assert input_page.entity1.save()
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
            assert each_value == backend_stanza[each_key]

    @pytest.mark.input
    # Verifies the frontend uneditable fields at time of edit of the example input one entity
    def test_example_input_one_edit_uneditable_field_name(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.edit_row("dummy_input_one")
        assert not input_page.entity1.name.is_editable()

    @pytest.mark.input
    # Verifies the frontend edit functionality of the example input one entity
    def test_example_input_one_edit_frontend_validation(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
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
        assert input_page.entity1.save()
        assert input_page.table.get_table()["dummy_input_one"] == { 
                'name': "dummy_input_one", 
                'account': 'test_input',
                'interval': '3600',
                'index': 'main',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }
    
    @pytest.mark.input
    # Verifies the backend edit functionality of the example input one entity
    def test_example_input_one_edit_backend_validation(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
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
        assert input_page.entity1.save()
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
            assert each_key in backend_stanza
            assert each_value == backend_stanza[each_key]

    @pytest.mark.input
    # Verifies the frontend default fields at time of clone for example input one entity
    def test_example_input_one_clone_default_values(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_one")
        assert input_page.entity1.name.get_value() == ""
        assert input_page.entity1.example_checkbox.is_checked()
        assert input_page.entity1.example_radio.get_value() == "Yes"
        assert input_page.entity1.single_select_group_test.get_value() == "Two"
        assert input_page.entity1.multiple_select_test.get_values() == ["A", "B"]
        assert input_page.entity1.interval.get_value() == "90"
        assert input_page.entity1.index.get_value() == "default"
        assert input_page.entity1.example_account.get_value() == "test_input"
        assert input_page.entity1.object.get_value() == "test_object"
        assert input_page.entity1.object_fields.get_value() == "test_field"
        assert input_page.entity1.order_by.get_value() == "LastModifiedDate"
        assert input_page.entity1.query_start_date.get_value() == "2020-12-11T20:00:32.000z"
        assert input_page.entity1.limit.get_value() == "1000"

    @pytest.mark.input
    # Verifies the frontend clone functionality of the example input one entity
    def test_example_input_one_clone_frontend_validation(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_one")
        input_page.entity1.name.set_value("Clone_Test")
        input_page.entity1.interval.set_value("180")
        input_page.entity1.limit.set_value("500")
        assert input_page.entity1.save()
        assert input_page.table.get_table()["Clone_Test"] == { 
                'name': 'Clone_Test', 
                'account': 'test_input',
                'interval': '180',
                'index': 'default',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }

    @pytest.mark.input
    # Verifies the backend clone functionality of the example input one entity
    def test_example_input_one_clone_backend_validation(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_one")
        input_page.entity1.name.set_value("Clone_Test")
        input_page.entity1.interval.set_value("180")
        input_page.entity1.limit.set_value("500")
        assert input_page.entity1.save()
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
            assert each_key in backend_stanza
            assert each_value == backend_stanza[each_key]

    @pytest.mark.input
    # Verifies the frontend delete functionlity
    def test_example_input_one_delete_row_frontend_validation(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.input_status_toggle("dummy_input_one", enable=False)
        input_page.table.delete_row("dummy_input_one")
        assert "dummy_input_one" not in input_page.table.get_table()

    @pytest.mark.input
    # Verifies the backend delete functionlity
    def test_example_input_one_delete_row_backend_validation(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.input_status_toggle("dummy_input_one", enable=False)
        input_page.table.delete_row("dummy_input_one")
        assert "example_input_one://dummy_input_one" not in input_page.backend_conf.get_all_stanzas().keys()

    @pytest.mark.input
    # Verifies close functionality at time of add
    def test_example_input_one_add_close_entity(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.close()

    @pytest.mark.input
    # Verifies close functionality at time of edit
    def test_example_input_one_edit_close_entity(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.edit_row("dummy_input_one")
        assert input_page.entity1.close()

    @pytest.mark.input
    # Verifies close functionality at time of clone
    def test_example_input_one_clone_close_entity(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_one")
        assert input_page.entity1.close()

    @pytest.mark.input
    # Verifies close functionality at time of delete
    def test_example_input_one_delete_close_entity(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        assert input_page.table.delete_row("dummy_input_one", close=True)

    @pytest.mark.input
    # Verifies cancel functionality at time of add
    def test_example_input_one_add_cancel_entity(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        assert input_page.entity1.cancel()

    @pytest.mark.input
    # Verifies cancel functionality at time of edit
    def test_example_input_one_edit_cancel_entity(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.edit_row("dummy_input_one")
        assert input_page.entity1.cancel()

    @pytest.mark.input
    # Verifies cancel functionality at time of clone
    def test_example_input_one_clone_cancel_entity(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_one")
        assert input_page.entity1.cancel()

    @pytest.mark.input
    # Verifies cancel functionality at time of delete
    def test_example_input_one_delete_cancel_entity(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        assert input_page.table.delete_row("dummy_input_one", cancel=True)

    @pytest.mark.input
    # Verifies by saving an entity with duplicate name it displays and error
    def test_example_input_one_add_duplicate_names(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input One")
        input_name = "dummy_input_one"
        input_page.entity1.name.set_value(input_name)
        assert input_page.entity1.save(expect_error=True) == "Name {} is already in use".format(input_name)
        assert input_page.entity1.close_error()

    @pytest.mark.input
    # Verifies by saving an entity with duplicate name at time of clone it displays and error
    def test_example_input_one_clone_duplicate_names(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_one")
        input_name = "dummy_input_one"
        input_page.entity1.name.set_value(input_name)
        assert input_page.entity1.save(expect_error=True) == "Name {} is already in use".format(input_name)
        assert input_page.entity1.close_error()



    ############################
    ### TEST CASES FOR TABLE ###
    ############################

    @pytest.mark.input
    # Verifies headers of input table
    def test_inputs_displayed_columns(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        header_list = ["", "Name", "Account", "Interval", "Index", "Status", "Actions"]
        assert list(input_page.table.get_headers()) == header_list

    @pytest.mark.input
    # Verifies input list dropdown
    def test_inputs_create_new_input_list_values(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        create_new_input_list = ["Example Input One", "Example Input Two"]
        assert input_page.create_new_input.get_inputs_list() == create_new_input_list

    @pytest.mark.input
    # Verifies input type filter list
    def test_inputs_input_type_list_values(self, ucc_smartx_configs, add_input_one, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        type_filter_list = ["All", "Example Input One", "Example Input Two"]
        assert input_page.type_filter.get_input_type_list() == type_filter_list
        input_page.type_filter.select_input_type("Example Input One", open_dropdown=False)
        assert input_page.table.get_row_count() == 1
        input_page.type_filter.select_input_type("Example Input Two")
        assert input_page.table.get_row_count() == 1

    @pytest.mark.input
    # Verifies enabled input should not delete
    def test_inputs_delete_enabled_input(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        assert input_page.table.delete_row("dummy_input_one", prompt_msg=True) == r"Can't delete enabled input"

    @pytest.mark.input
    # Verifies pagination list
    def test_inputs_pagination_list(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        assert input_page.pagination.get_pagination_list() == ['10 Per Page','25 Per Page','50 Per Page']
    

    @pytest.mark.input
    # Verifies the expand functionality of the inputs table
    def test_inputs_more_info(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        assert input_page.table.get_more_info("dummy_input_one") == {
            'Name': 'dummy_input_one', 
            'Interval': '90',
            'Index': 'default',
            'Status': 'Enabled',
            'Example Account': 'test_input',
            'Object': 'test_object',
            'Object Fields': 'test_field',
            'Order By': 'LastModifiedDate',
            'Query Start Date': '2020-12-11T20:00:32.000z',
            'Limit': '1000',
       }

    @pytest.mark.input
    # Verifies the enable and disable functionality of the input
    def test_inputs_enable_disable(self, ucc_smartx_configs, add_input_one):
        input_page = InputPage(ucc_smartx_configs)
        assert input_page.table.input_status_toggle("dummy_input_one", enable=False)
        assert input_page.table.input_status_toggle("dummy_input_one", enable=True)

    @pytest.mark.input
    # Verifies the filter functionality (Negative)
    def test_inputs_filter_functionality_negative(self, ucc_smartx_configs, add_input_one, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.set_filter("hello")
        assert input_page.table.get_count_title() == "{} Inputs".format(input_page.table.get_row_count())
        input_page.table.clean_filter()

    @pytest.mark.input
    # Verifies the filter functionality (Positive)
    def test_inputs_filter_functionality_positive(self, ucc_smartx_configs, add_input_one, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.set_filter("dummy")
        assert input_page.table.get_count_title() == "{} Inputs".format(input_page.table.get_row_count())
        input_page.table.clean_filter()

    @pytest.mark.input
    # Verifies count on table
    def test_inputs_count(self, ucc_smartx_configs, add_input_one, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        assert input_page.table.get_count_title() == "{} Inputs".format(input_page.table.get_row_count())
    
    @pytest.mark.input
    # Verifies sorting functionality for name column
    def test_inputs_sort_functionality(self, ucc_smartx_configs, add_input_one, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.pagination.select_page_option("50 Per Page")
        input_page.table.sort_column("Name")
        sort_order = input_page.table.get_sort_order()
        column_values = list(input_page.table.get_column_values("Name"))
        column_values = list(str(item) for item in column_values)
        sorted_values = sorted(column_values , key = str.lower)
        assert sort_order["header"].lower() == "name"
        assert column_values==sorted_values
        assert sort_order["ascending"]

    @pytest.mark.input
    # Verifies pagination functionality by creating 100 accounts
    def test_inputs_pagination(self, ucc_smartx_configs, add_multiple_inputs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.open()
        assert input_page.pagination.select_page_option("50 Per Page")
        assert input_page.table.switch_to_page(2)
        assert input_page.table.switch_to_prev()
        assert input_page.table.switch_to_next()

    ##########################################
    #### TEST CASES FOR EXAMPLE INPUT TWO ####
    ##########################################

    @pytest.mark.input
    # Verifies required field name in Example Input Two
    def test_example_input_two_required_field_name(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        assert input_page.entity2.save(expect_error=True) == r"Field Name is required"
        assert input_page.entity2.close_error()

    @pytest.mark.input
    # Verifies the name field should not be more than 100 characters
    def test_example_input_two_valid_length_name(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        name_value = "a"* 101
        input_page.entity2.name.set_value(name_value)
        assert input_page.entity2.save(expect_error=True) == r"Length of input name should be between 1 and 100"
        assert input_page.entity2.close_error()

    @pytest.mark.input
    # Verifies whether adding special characters, name field displays validation error
    def test_example_input_two_valid_input_name(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("$$test_name_two")
        assert input_page.entity2.save(expect_error=True) == r"Input Name must begin with a letter and consist exclusively of alphanumeric characters and underscores."
        assert input_page.entity2.close_error()

    @pytest.mark.input
    # Verifies required field interval in Example Input Two
    def test_example_input_two_required_field_interval(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("test_name_two")
        assert input_page.entity2.save(expect_error=True) == r"Field Interval is required"
        assert input_page.entity2.close_error()

    @pytest.mark.input
    # Verifies whether adding non numeric values, intreval field displays validation error
    def test_example_input_two_valid_input_interval(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("test_name_two")
        input_page.entity2.interval.set_value("abc")
        assert input_page.entity2.save(expect_error=True) == r"Interval must be an integer."
        assert input_page.entity2.close_error()

    @pytest.mark.input
    # Verifies required field index in Example Input Two
    def test_example_input_two_required_field_index(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("test_name_two")
        input_page.entity2.interval.set_value("120")
        input_page.entity2.index.cancel_selected_value()
        assert input_page.entity2.save(expect_error=True) == r"Field Index is required"
        assert input_page.entity2.close_error()

    @pytest.mark.input
    # Verifies default value of field index in Example Input Two
    def test_example_input_two_default_value_index(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        default_index = "default"
        input_page.create_new_input.select("Example Input Two")
        assert input_page.entity2.index.get_value() == default_index

    @pytest.mark.input
    # Verifies required field Account in Example Input Two
    def test_example_input_two_required_field_example_example_account(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("test_name_two")
        input_page.entity2.interval.set_value("120")
        assert input_page.entity2.save(expect_error=True) == r"Field Example Account is required"
        assert input_page.entity2.close_error()

    @pytest.mark.input
    # Verifies required field Example Multiple Select in Example Input Two
    def test_example_input_two_required_field_example_multiple_select(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("test_name_two")
        input_page.entity2.interval.set_value("120")
        input_page.entity2.example_account.select("test_input")
        assert input_page.entity2.save(expect_error=True) == r"Field Example Multiple Select is required"
        assert input_page.entity2.close_error()

    @pytest.mark.input
    # Verifies values of Multiple Select Test dropdown in Example Input Two
    def test_example_input_two_list_example_multiple_select(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        example_multiple_select_list = ["Option One", "Option Two"]
        assert list(input_page.entity2.example_multiple_select.list_of_values()) == example_multiple_select_list

    @pytest.mark.input
    # Verifies selected single value of Multiple Select Test dropdown in Example Input Two
    def test_example_input_two_select_select_value_example_multiple_select(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        selected_value = ["Option One"]
        input_page.create_new_input.select("Example Input Two")
        for each in selected_value:
            input_page.entity2.example_multiple_select.select(each)
        assert input_page.entity2.example_multiple_select.get_values() == selected_value

    @pytest.mark.input
    # Verifies selected multiple values of Multiple Select Test dropdown in Example Input Two
    def test_example_input_two_select_multiple_values_example_multiple_select(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        selected_values = ["Option One", "Option Two"]
        input_page.create_new_input.select("Example Input Two")
        for each in selected_values:
            input_page.entity2.example_multiple_select.select(each)
        assert input_page.entity2.example_multiple_select.get_values() == selected_values

    @pytest.mark.input
    # Verifies Check in example checkbox in Example Input Two
    def test_example_input_two_checked_example_checkbox(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        assert input_page.entity2.example_checkbox.check()

    @pytest.mark.input
    # Verifies Uncheck in example checkbox in Example Input Two
    def test_example_input_two_unchecked_example_checkbox(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.example_checkbox.check()
        assert input_page.entity2.example_checkbox.uncheck()   

    @pytest.mark.input
    # Verifies default value of example radio in Example Input Two
    def test_example_input_two_required_field_example_radio(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("test_name_two")
        input_page.entity2.interval.set_value("120")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.example_multiple_select.select("Option One")
        assert input_page.entity2.save(expect_error=True) == r"Field Example Radio is required"

    @pytest.mark.input
    # Verifies default value of example radio in Example Input Two
    def test_example_input_two_select_value_example_radio(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.example_radio.select("No")
        assert input_page.entity2.example_radio.get_value() == "No"

    @pytest.mark.input
    # Verifies whether adding wrong format, Query Start Date field displays validation error
    def test_example_input_two_valid_input_query_start_date(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_page.entity2.name.set_value("test_name_two")
        input_page.entity2.interval.set_value("120")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.example_multiple_select.select("Option One")
        input_page.entity2.example_radio.select("Yes")
        input_page.entity2.query_start_date.set_value("2020/01/01")
        assert input_page.entity2.save(expect_error=True) == r"Invalid date and time format"
        assert input_page.entity2.close_error()

    ###################################
    #### TEST CASES FOR ENTITY TWO ####
    ###################################

    @pytest.mark.input
    # Verifies the frontend after adding a Example Input Two
    def test_example_input_two_add_frontend_validation(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
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
        assert input_page.entity2.save()
        assert input_page.table.get_table()["Test_Add"] == { 
                'name': 'Test_Add', 
                'account': 'test_input',
                'interval': '90',
                'index': 'main',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }
        url = input_page._get_input_endpoint()

    @pytest.mark.input
    # Verifies the backend after adding a Example Input Two
    def test_example_input_two_add_backend_validation(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
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
        assert input_page.entity2.save()
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
            assert each_key in backend_stanza
            assert each_value == backend_stanza[each_key]

    @pytest.mark.input
    # Verifies the frontend uneditable fields at time of edit of the Example Input Two entity
    def test_example_input_two_edit_uneditable_field_name(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.edit_row("dummy_input_two")
        assert not input_page.entity2.name.is_editable()

    @pytest.mark.input
    # Verifies the frontend edit functionality of the Example Input Two entity
    def test_example_input_two_edit_frontend_validation(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.edit_row("dummy_input_two")
        input_page.entity2.example_checkbox.uncheck()
        input_page.entity2.example_radio.select("Yes")
        input_page.entity2.example_multiple_select.deselect("Option One")
        input_page.entity2.interval.set_value("3600")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-20-20T20:20:20.000z")
        assert input_page.entity2.save()
        assert input_page.table.get_table()["dummy_input_two"] == { 
                'name': "dummy_input_two", 
                'account': 'test_input',
                'interval': '3600',
                'index': 'main',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }
    
    @pytest.mark.input
    # Verifies the backend edit functionality of the Example Input Two entity
    def test_example_input_two_edit_backend_validation(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.edit_row("dummy_input_two")
        input_page.entity2.example_checkbox.uncheck()
        input_page.entity2.example_radio.select("Yes")
        input_page.entity2.example_multiple_select.deselect("Option One")
        input_page.entity2.interval.set_value("3600")
        input_page.entity2.example_account.select("test_input")
        input_page.entity2.query_start_date.set_value("2020-20-20T20:20:20.000z")
        assert input_page.entity2.save()
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
            assert each_key in backend_stanza
            assert each_value == backend_stanza[each_key]

    @pytest.mark.input
    # Verifies the frontend default fields at time of clone for Example Input Two entity
    def test_example_input_two_clone_default_values(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_two")
        assert input_page.entity2.name.get_value() == ""
        assert input_page.entity2.example_checkbox.is_checked()
        assert input_page.entity2.example_radio.get_value() == "No"
        assert input_page.entity2.example_multiple_select.get_values() == ["Option One", "Option Two"]
        assert input_page.entity2.interval.get_value() == "100"
        assert input_page.entity2.index.get_value() == "main"
        assert input_page.entity2.example_account.get_value() == "test_input"
        assert input_page.entity2.query_start_date.get_value() == "2016-10-10T12:10:15.000z"

    @pytest.mark.input
    # Verifies the frontend clone functionality of the Example Input Two entity
    def test_example_input_two_clone_frontend_validation(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_two")
        input_page.entity2.name.set_value("Clone_Test")
        input_page.entity2.interval.set_value("180")
        assert input_page.entity2.save()
        assert input_page.table.get_table()["Clone_Test"] == { 
                'name': 'Clone_Test', 
                'account': 'test_input',
                'interval': '180',
                'index': 'main',
                'status': 'Enabled',
                'actions': 'Edit | Clone | Delete',
            }

    @pytest.mark.input
    # Verifies the backend clone functionality of the Example Input Two entity
    def test_example_input_two_clone_backend_validation(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_two")
        input_page.entity2.name.set_value("Clone_Test")
        input_page.entity2.interval.set_value("180")
        assert input_page.entity2.save()
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
            assert each_key in backend_stanza
            assert each_value == backend_stanza[each_key]

    @pytest.mark.input
    # Verifies the frontend delete functionlity
    def test_example_input_two_delete_row_frontend_validation(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.input_status_toggle("dummy_input_two", enable=False)
        input_page.table.delete_row("dummy_input_two")
        assert "dummy_input_two" not in input_page.table.get_table()

    @pytest.mark.input
    # Verifies the backend delete functionlity
    def test_example_input_two_delete_row_backend_validation(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.input_status_toggle("dummy_input_two", enable=False)
        input_page.table.delete_row("dummy_input_two")
        assert "example_input_two://dummy_input_two" not in input_page.backend_conf.get_all_stanzas().keys()

    @pytest.mark.input
    # Verifies close functionality at time of add
    def test_example_input_two_add_close_entity(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        assert input_page.entity2.close()

    @pytest.mark.input
    # Verifies close functionality at time of edit
    def test_example_input_two_edit_close_entity(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.edit_row("dummy_input_two")
        assert input_page.entity2.close()

    @pytest.mark.input
    # Verifies close functionality at time of clone
    def test_example_input_two_clone_close_entity(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_two")
        assert input_page.entity2.close()

    @pytest.mark.input
    # Verifies close functionality at time of delete
    def test_example_input_two_delete_close_entity(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        assert input_page.table.delete_row("dummy_input_two", close=True)

    @pytest.mark.input
    # Verifies cancel functionality at time of add
    def test_example_input_two_add_cancel_entity(self, ucc_smartx_configs):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        assert input_page.entity2.cancel()

    @pytest.mark.input
    # Verifies cancel functionality at time of edit
    def test_example_input_two_edit_cancel_entity(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.edit_row("dummy_input_two")
        assert input_page.entity2.cancel()

    @pytest.mark.input
    # Verifies cancel functionality at time of clone
    def test_example_input_two_clone_cancel_entity(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_two")
        assert input_page.entity2.cancel()

    @pytest.mark.input
    # Verifies cancel functionality at time of delete
    def test_example_input_two_delete_cancel_entity(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        assert input_page.table.delete_row("dummy_input_two", cancel=True)

    @pytest.mark.input
    # Verifies by saving an entity with duplicate name it displays and error
    def test_example_input_two_add_duplicate_names(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.create_new_input.select("Example Input Two")
        input_name = "dummy_input_two"
        input_page.entity2.name.set_value(input_name)
        assert input_page.entity2.save(expect_error=True) == "Name {} is already in use".format(input_name)
        assert input_page.entity2.close_error()

    @pytest.mark.input
    # Verifies by saving an entity with duplicate name at time of clone it displays and error
    def test_example_input_two_clone_duplicate_names(self, ucc_smartx_configs, add_input_two):
        input_page = InputPage(ucc_smartx_configs)
        input_page.table.clone_row("dummy_input_two")
        input_name = "dummy_input_two"
        input_page.entity2.name.set_value(input_name)
        assert input_page.entity2.save(expect_error=True) == "Name {} is already in use".format(input_name)
        assert input_page.entity2.close_error()
