from ucc_smartx.base_test import UccTester
from ucc_smartx.backend_confs import BackendConf
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


ACCOUNT_CONFIG = {
    'name': 'TestAccount',
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

@pytest.fixture
def add_input(ucc_smartx_configs):
    input_page = InputPage(ucc_smartx_configs)
    url = input_page._get_input_endpoint()
    kwargs = {
        'name': 'example_input_one://dummy_input_one',
        'account':'TestAccount',
        'input_one_checkbox': '1',
        'input_one_radio': '1',
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
def add_account(ucc_smartx_configs):
    account = AccountPage(ucc_smartx_configs)
    url = account._get_account_endpoint()
    kwargs = ACCOUNT_CONFIG
    yield account.backend_conf.post_stanza(url, kwargs)

@pytest.fixture
def add_multiple_account(ucc_smartx_configs):
    account = AccountPage(ucc_smartx_configs)
    url = account._get_account_endpoint()
    for i in range(12):
        kwargs = copy.deepcopy(ACCOUNT_CONFIG)
        kwargs['name'] = kwargs['name'] + str(i)
        account.backend_conf.post_stanza(url, kwargs)

@pytest.fixture(autouse=True)
def delete_accounts(ucc_smartx_configs):
    yield
    account = AccountPage(ucc_smartx_configs)
    account.backend_conf.delete_all_stanzas()
    

class TestAccount(UccTester):
    
    @pytest.mark.account
    def test_account_sort_name(self, ucc_smartx_configs, add_multiple_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.sort_column("Name")
        sort_order = account.table.get_sort_order()
        x = list(account.table.get_column_values("Name"))
        x = list(str(item) for item in x)
        y = sorted(x , key = str.lower)
        assert sort_order["header"].lower() == "name"
        assert x==y
        assert sort_order["ascending"]
        
    @pytest.mark.account
    def test_account_title_count(self, ucc_smartx_configs, add_multiple_account):
        account = AccountPage(ucc_smartx_configs)
        no_of_accounts = account.table.get_count_title()
        total_items = len(account.backend_conf.get_all_stanzas())
        assert no_of_accounts == "{} Items".format(total_items)

    @pytest.mark.account
    def test_add_account_frontend(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG['name'])
        account.entity.username.set_value(ACCOUNT_CONFIG['username'])
        account.entity.multiple_select.select("Option One")
        account.entity.password.set_value(ACCOUNT_CONFIG['password'])
        account.entity.security_token.set_value("TestToken")
        assert account.entity.save()
        assert account.table.get_table()[ACCOUNT_CONFIG['name']] == {
                'name': ACCOUNT_CONFIG['name'],
                'auth type': 'basic',
                'actions': 'Edit | Clone | Delete'
            }

    @pytest.mark.account
    def test_account_username_required_fields(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        assert account.entity.save(expect_error=True) == 'Field Username is required'

    @pytest.mark.account
    def test_account_password_required_fields(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        assert account.entity.save(expect_error=True) == 'Field Password is required'

    @pytest.mark.account
    def test_account_name_required_fields(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        assert account.entity.save(expect_error=True) == 'Field Name is required'

    @pytest.mark.account
    def test_multi_select_required_fields(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value("TestMultiAccount")
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        assert account.entity.save(expect_error=True) == 'Field Example Multiple Select is required'
    
    @pytest.mark.account
    def test_account_client_id_required_fields(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.auth_key.select('OAuth 2.0 Authentication')
        assert account.entity.save(expect_error=True) == 'Field Client Id is required'
    
    @pytest.mark.account
    def test_account_client_secret_required_fields(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.auth_key.select('OAuth 2.0 Authentication')
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        account.entity.multiple_select.select("Option One")
        account.entity.client_id.set_value("TestClientId")
        assert account.entity.save(expect_error=True) == 'Field Client Secret is required'

    @pytest.mark.account
    def test_account_name_start_with_number_required_fields(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        account.entity.name.set_value("123TestAccount")
        assert account.entity.save(expect_error=True) == 'Name must begin with a letter and consist exclusively of alphanumeric characters and underscores.'
    
    @pytest.mark.account
    def test_account_name_length_validation(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        account.entity.name.set_value("TestUserTestUserTestUserTestUserTestUserTestUserTestUserTestUser")
        assert account.entity.save(expect_error=True) == 'Length of ID should be between 1 and 50'

    @pytest.mark.account
    def test_environment_default_value(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        assert account.entity.environment.get_value() == "Value1"

    @pytest.mark.account
    def test_account_enviornment_list(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        assert set(account.entity.environment.list_of_values()) == {"Value1", "Value2", "Other"}

    @pytest.mark.account
    def test_account_auth_key_default_value(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        assert account.entity.auth_key.get_value() == "basic"

    @pytest.mark.account
    def test_account_auth_list(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        assert set(account.entity.auth_key.list_of_values()) == {"Basic Authentication", "OAuth 2.0 Authentication"}

    @pytest.mark.account
    def test_account_example_checkbox_checked(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.example_checkbox.check()
        assert account.entity.example_checkbox.is_checked() == True
        account.entity.example_checkbox.uncheck()
        assert account.entity.example_checkbox.is_checked() == False
        
    @pytest.mark.account
    def test_account_entity_close(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        assert account.entity.close()

    @pytest.mark.account
    def test_account_entity_cancel(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        assert account.entity.cancel()

    @pytest.mark.account
    def test_delete_close(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.delete_row(ACCOUNT_CONFIG["name"])
        assert account.entity.close()
        
    @pytest.mark.account
    def test_delete_cancel(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.delete_row(ACCOUNT_CONFIG["name"])
        assert account.entity.cancel()
    
    @pytest.mark.account
    def test_edit_close(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        assert account.entity.close()
        
    @pytest.mark.account
    def test_edit_cancel(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        assert account.entity.cancel()
    
    @pytest.mark.account
    def test_clone_close(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        assert account.entity.close()

    @pytest.mark.account
    def test_clone_cancel(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        assert account.entity.cancel()
        
    @pytest.mark.account
    def test_verify_duplicate_account_name(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        account.entity.multiple_select.select("Option One")
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        account.entity.account_radio.select("Yes")
        assert account.entity.save(expect_error=True) == 'Name TestAccount is already in use'
    
    @pytest.mark.account
    def test_account_delete_row(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.delete_row(ACCOUNT_CONFIG["name"])
        assert ACCOUNT_CONFIG["name"] not in account.table.get_table()

    @pytest.mark.account
    def test_account_name_is_not_editable(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        assert account.entity.name.is_editable() == False
    
    @pytest.mark.account
    def test_account_edit_frontend(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        account.entity.environment.select("Value2")
        account.entity.multiple_select.select("Option Two")
        account.entity.username.set_value("TestEditUser")
        account.entity.password.set_value("TestEditPassword")
        account.entity.security_token.set_value("TestEditToken")
        account.entity.account_radio.select("No")
        assert account.entity.save()
        assert account.table.get_table()[ACCOUNT_CONFIG["name"]] == { 
                'name': 'TestAccount', 
                'auth type': 'basic',
                'actions': 'Edit | Clone | Delete'
            }

    @pytest.mark.account
    def test_account_clone_frontend(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        assert account.entity.name.get_value() == ""
        account.entity.name.set_value("TestAccount2")
        account.entity.username.set_value("TestUserClone")
        account.entity.password.set_value("TestPasswordClone")
        account.entity.security_token.set_value("TestTokenClone")
        account.entity.account_radio.select("Yes")
        assert account.entity.save()
        assert account.table.get_table()["TestAccount2"] == { 
                'name': 'TestAccount2', 
                'auth type': 'basic',
                'actions': 'Edit | Clone | Delete'
            }
    
    @pytest.mark.account
    def test_add_account_backend_verification(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        account.entity.open()
        account.entity.name.set_value(ACCOUNT_CONFIG["name"])
        account.entity.username.set_value(ACCOUNT_CONFIG["username"])
        account.entity.multiple_select.select("Option One")
        account.entity.password.set_value(ACCOUNT_CONFIG["password"])
        account.entity.security_token.set_value(ACCOUNT_CONFIG["token"])
        assert account.entity.save()
        assert account.backend_conf.get_stanza(ACCOUNT_CONFIG["name"]) == {
                'account_checkbox': '0',
                'account_multiple_select' : ACCOUNT_CONFIG['account_multiple_select'],
                'account_radio' : '1',
                'auth_type' : ACCOUNT_CONFIG['auth_type'],
                'username' : ACCOUNT_CONFIG["username"],
                'custom_endpoint': ACCOUNT_CONFIG['custom_endpoint'],
                'disabled': False,
                'password': '******',
                'token': '******'
            }

    @pytest.mark.account
    def test_edit_account_backend_verification(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.edit_row(ACCOUNT_CONFIG["name"])
        account.entity.multiple_select.select("Option Two")
        account.entity.username.set_value("TestEditUser")
        account.entity.password.set_value("TestEditPassword")
        account.entity.security_token.set_value("TestEditToken")
        account.entity.account_radio.select("No")
        account.entity.save()
        assert account.backend_conf.get_stanza(ACCOUNT_CONFIG["name"]) == {
                'account_checkbox': '1',
                'account_multiple_select' : 'one,two',
                'account_radio' : '0',
                'auth_type' : 'basic',
                'username' : 'TestEditUser',
                'custom_endpoint': 'login.example.com',
                'disabled': False,
                'password': '******',
                'token': '******'
            }
    
    @pytest.mark.account
    def test_clone_account_backend_verification(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.clone_row(ACCOUNT_CONFIG["name"])
        account.entity.name.set_value("TestAccountClone")
        account.entity.multiple_select.select("Option Two")
        account.entity.username.set_value("TestCloneUser")
        account.entity.password.set_value("TestClonePassword")
        account.entity.security_token.set_value("TestCloneToken")
        account.entity.account_radio.select("No")
        account.entity.save()
        assert account.backend_conf.get_stanza("TestAccountClone") == {
                'account_checkbox': '1',
                'account_multiple_select' : 'one,two',
                'account_radio' : '0',
                'auth_type' : 'basic',
                'username' : 'TestCloneUser',
                'custom_endpoint': 'login.example.com',
                'disabled': False,
                'password': '******',
                'token': '******'
            }
    
    @pytest.mark.account
    def test_delete_row_backend_verification(self, ucc_smartx_configs, add_account):
        account = AccountPage(ucc_smartx_configs)
        account.table.delete_row(ACCOUNT_CONFIG["name"])
        assert ACCOUNT_CONFIG["name"] not in account.backend_conf.get_all_stanzas().keys()
    
    @pytest.mark.account
    def test_account_pagination(self, ucc_smartx_configs, add_multiple_account):
        account = AccountPage(ucc_smartx_configs)
        name_column_page1 = account.table.get_column_values("name")
        account.table.switch_to_next()
        name_column_page2 = account.table.get_column_values("name")
        assert name_column_page1 != name_column_page2

    @pytest.mark.account
    def test_account_page_help_link(self, ucc_smartx_configs):
        account = AccountPage(ucc_smartx_configs)
        go_to_link = "https://docs.splunk.com/Documentation"
        account.entity.open()
        assert account.entity.help_link.go_to_link() == go_to_link

    @pytest.mark.account
    def test_delete_input_used_account(self, ucc_smartx_configs, add_account, add_input):
        account = AccountPage(ucc_smartx_configs)
        account.table.delete_row(ACCOUNT_CONFIG["name"])
        assert account.table.delete_row(ACCOUNT_CONFIG["name"], prompt_msg=True) == r'TestAccount cannot be deleted because it is in use'
    