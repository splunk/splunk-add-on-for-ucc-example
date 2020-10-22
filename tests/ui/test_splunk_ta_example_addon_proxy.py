from pytest_splunk_addon_ui_smartx.base_test import UccTester
from pytest_splunk_addon_ui_smartx.pages.proxy import Proxy
import pytest
import time
import re
import random
import os

TA_NAME = "Splunk_TA_UCCExample"
TA_CONF = "splunk_ta_uccexample_settings"

DEFAULT_CONFIGURATION = {
    'proxy_enabled': 0,
    'proxy_password': '',
    'proxy_port': '',
    'proxy_rdns': 0,
    'proxy_type': 'http',
    'proxy_url': '',
    'proxy_username': '',

}

@pytest.fixture(autouse=True)
def reset_configuration(ucc_smartx_rest_helper):
    yield
    proxy = Proxy(TA_NAME, TA_CONF,ucc_smartx_rest_helper = ucc_smartx_rest_helper)
    proxy.backend_conf.update_parameters(DEFAULT_CONFIGURATION)

class TestProxy(UccTester):

    @pytest.mark.proxy
    def test_proxy_default_configs(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the default proxy configurations"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            proxy.proxy_enable.is_checked,
            False
            )
        self.assert_util(
            proxy.dns_enable.is_checked,
            False
            )
        self.assert_util(
            proxy.type.get_value,
            "http"
            )
        self.assert_util(
            proxy.host.get_value,
            ""
            )
        self.assert_util(
            proxy.port.get_value,
            ""
            )
        self.assert_util(
            proxy.username.get_value,
            ""
            )
        self.assert_util(
            proxy.password.get_value,
            ""
            )

    @pytest.mark.proxy
    def test_proxy_required_field_host(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether the host field in proxy is required and displays an error if left empty"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        proxy.proxy_enable.check()
        proxy.type.select("http")
        proxy.dns_enable.check()
        proxy.port.set_value("3285")
        proxy.username.set_value("Username")
        proxy.password.set_value("Password")        
        self.assert_util(
            proxy.save,
            "Proxy Host can not be empty",
            left_args={'expect_error': True}
            )
        self.assert_util(proxy.close_error, True)

    @pytest.mark.proxy
    def test_proxy_host_valid_input(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies if host contains special characters displays an error"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        proxy.host.set_value("abc$$")
        self.assert_util(
            proxy.save,
            "Proxy Host should not have special characters",
            left_args={'expect_error': True}
            )
        self.assert_util(proxy.close_error, True)

    @pytest.mark.proxy
    def test_proxy_host_field_length_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies host field length validation"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        host_value = "a" * 4097
        proxy.host.set_value(host_value)
        self.assert_util(
            proxy.save,
            "Max host length is 4096",
            left_args={'expect_error': True}
            )
        self.assert_util(proxy.close_error, True)

    @pytest.mark.proxy
    def test_proxy_required_field_port(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether the proxy field is required and displays an error if left empty"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        proxy.proxy_enable.check()
        proxy.type.select("http")
        proxy.dns_enable.check()
        proxy.host.set_value("host")
        proxy.username.set_value("Username")
        proxy.password.set_value("Password")
        self.assert_util(
            proxy.save,
            "Proxy Port can not be empty",
            left_args={'expect_error': True}
            )
        self.assert_util(proxy.close_error, True)


    @pytest.mark.proxy
    def test_proxy_port_field_valid_range(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether the proxy field only allows numeric values"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        proxy.host.set_value("abc")
        proxy.port.set_value("abc")
        self.assert_util(
            proxy.save,
            "Field Port is not a number",
            left_args={'expect_error': True}
            )
        self.assert_util(proxy.close_error, True)

    @pytest.mark.proxy
    def test_proxy_port_field_out_of_range(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ verifies out of range port value"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        proxy.host.set_value("abc")
        proxy.port.set_value("65536")
        self.assert_util(
            proxy.save,
            "Field Port should be within the range of [1 and 65535]",
            left_args={'expect_error': True}
            )
        self.assert_util(proxy.close_error, True)

    @pytest.mark.proxy
    def test_proxy_list_proxy_types(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ This test case checks list of proxy types present in the drop down"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        self.assert_util(
            proxy.type.list_of_values(),
            ["http", "socks4", "socks5"]
            )

    @pytest.mark.proxy
    def test_proxy_required_field_proxy_type(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies whether proxy type is required and displays an error if left empty"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        proxy.proxy_enable.check()
        proxy.type.select("http")
        proxy.dns_enable.check()
        proxy.host.set_value("host")
        proxy.port.set_value("3285")
        proxy.username.set_value("Username")
        proxy.password.set_value("Password")
        proxy.type.cancel_selected_value()
        self.assert_util(
            proxy.save,
            "Proxy type can not be empty",
            left_args={'expect_error': True}
            )
        self.assert_util(proxy.close_error, True)

    @pytest.mark.proxy
    def test_proxy_username_field_length_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """Verifies username field length validation"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        username_value = "a" * 51
        proxy.host.set_value("abc")
        proxy.port.set_value("65535")
        proxy.username.set_value(username_value)
        self.assert_util(
            proxy.save,
            "Max length of username is 50",
            left_args={'expect_error': True}
            )
        self.assert_util(proxy.close_error, True)

    @pytest.mark.proxy
    def test_proxy_encrypted_field_password(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies if the password field is masked or not in the Textbox"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        textbox_type = proxy.password.get_type()
        self.assert_util(
            textbox_type ,
            'password'
            )

    @pytest.mark.proxy
    def test_proxy_frontend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the proxy is saved properly in frontend after saving it"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        proxy.proxy_enable.check()
        proxy.type.select("http")
        proxy.dns_enable.check()
        proxy.host.set_value("host")
        proxy.port.set_value("3285")
        proxy.username.set_value("Username")
        proxy.password.set_value("Password")
        self.assert_util(proxy.save, True)

    @pytest.mark.proxy
    def test_proxy_backend_validation(self, ucc_smartx_selenium_helper, ucc_smartx_rest_helper):
        """ Verifies the proxy is saved properly in frontend after saving it"""
        proxy = Proxy(TA_NAME, TA_CONF, ucc_smartx_selenium_helper, ucc_smartx_rest_helper)
        proxy.proxy_enable.check()
        proxy.type.select("http")
        proxy.dns_enable.check()
        proxy.host.set_value("host")
        proxy.port.set_value("3285")
        proxy.username.set_value("Username")
        proxy.password.set_value("Password")
        proxy.save()
        self.assert_util(
            proxy.backend_conf.get_stanza,
            {
                'disabled': False,
                'proxy_enabled': '1',
                'proxy_port': '3285', 
                'proxy_rdns': '1',
                'proxy_type': 'http',
                'proxy_url': 'host',
                'proxy_password': '******',
                'proxy_username': 'Username'
            }
            )