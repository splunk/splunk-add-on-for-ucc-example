from ucc_smartx.base_test import UccTester
from ucc_smartx.pages.proxy import Proxy
import pytest
import time
import re
import random
import os


class TestProxy(UccTester):

    @pytest.mark.proxy
    # Verifies the default proxy configurations
    def test_proxy_default_configs(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        assert proxy.proxy_enable.is_checked() == False
        assert proxy.dns_enable.is_checked() == False
        assert proxy.type.get_value() == "http"

    @pytest.mark.proxy
    # Verifies whether the host field in proxy is required and displays an error if left empty
    def test_proxy_required_field_host(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        proxy.proxy_enable.check()
        assert proxy.save(expect_error=True) == "Proxy Host can not be empty"
        assert proxy.close_error()

    @pytest.mark.proxy
    # Verifies if host contains special characters displays an error
    def test_proxy_host_valid_input(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        proxy.host.set_value("abc$$")
        assert proxy.save(expect_error=True) == "Proxy Host should not have special characters"
        assert proxy.close_error()

    @pytest.mark.proxy
    # Verifies host field length validation
    def test_proxy_host_field_length_validation(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        host_value = "a" * 4097
        proxy.host.set_value(host_value)
        assert proxy.save(expect_error=True) == "Max host length is 4096"
        assert proxy.close_error()

    @pytest.mark.proxy
    # Verifies whether the proxy field is required and displays an error if left empty
    def test_proxy_required_field_port(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        proxy.proxy_enable.check()
        proxy.host.set_value("abc")
        assert proxy.save(expect_error=True) == "Proxy Port can not be empty"
        assert proxy.close_error()


    @pytest.mark.proxy
    # Verifies whether the proxy field only allows numeric values
    def test_proxy_port_field_numeric_values(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        proxy.host.set_value("abc")
        proxy.port.set_value("abc")
        assert proxy.save(expect_error=True) == "Field Port is not a number"
        assert proxy.close_error()

    @pytest.mark.proxy
    # verifies out of range port value
    def test_proxy_port_field_out_of_range(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        proxy.host.set_value("abc")
        proxy.port.set_value("65536")
        assert proxy.save(expect_error=True) == "Field Port should be within the range of [1 and 65535]"
        assert proxy.close_error()

    @pytest.mark.proxy
    # This test case checks list of proxy types present in the drop down
    def test_proxy_list(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        assert set(proxy.type.list_of_values()) == {"http", "socks4", "socks5"}

    @pytest.mark.proxy
    # Verifies whether proxy type is required and displays an error if left empty
    def test_proxy_required_field_proxy_type(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        proxy.host.set_value("abc")
        proxy.port.set_value("1111")
        proxy.type.cancel_selected_value()
        assert proxy.save(expect_error=True) == "Field Proxy Type is required"
        assert proxy.close_error()

    @pytest.mark.proxy
    def test_proxy_username_field_length_validation(self, ucc_smartx_configs):
    # Verifies username field length validation
        proxy = Proxy(ucc_smartx_configs)
        username_value = "a" * 51
        proxy.host.set_value("abc")
        proxy.port.set_value("65535")
        proxy.username.set_value(username_value)
        assert proxy.save(expect_error=True) == "Max length of username is 50"
        assert proxy.close_error()

    @pytest.mark.proxy
    # Verifies the proxy is saved properly in frontend after saving it
    def test_proxy_frontend(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        proxy.proxy_enable.check()
        proxy.proxy_enable.uncheck()
        proxy.type.select("http")
        proxy.dns_enable.check()
        proxy.host.set_value("host")
        proxy.port.set_value("3285")
        proxy.username.set_value("Username")
        proxy.password.set_value("Password")
        assert proxy.save()

    @pytest.mark.proxy
    # Verifies the proxy is saved properly in frontend after saving it
    def test_proxy_backend(self, ucc_smartx_configs):
        proxy = Proxy(ucc_smartx_configs)
        assert proxy.backend_conf.get_stanza() == {
            'disabled': False,
            'proxy_enabled': '0',
            'proxy_port': '3285', 
            'proxy_rdns': '1',
            'proxy_type': 'http',
            'proxy_url': 'host',
            'proxy_password': '******',
            'proxy_username': 'Username'
            }