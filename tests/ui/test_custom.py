from pytest_splunk_addon_ui_smartx.base_test import UccTester
from .Example_UccLib.custom import Custom
import pytest
import time
import re
import random
import os

DEFAULT_CONFIGURATION = {
    'test_number': '',
    'test_regex': '',
    'test_string': '',
    'test_email': '',
    'test_ipv4': '',
    'test_date': '',
    'test_url': '',
    'test_radio': 'Yes',
    'test_multiselect': ''
}

@pytest.fixture(autouse=True)
def reset_configuration(ucc_smartx_configs):
    yield
    custom = Custom(ucc_smartx_configs)
    custom.backend_conf.update_parameters(DEFAULT_CONFIGURATION)

class TestCustom(UccTester):

    @pytest.mark.custom
    # This test case checks the validates frontend save in custom tab
    def test_custom_frontend_validation(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        custom.test_number.set_value("7")
        custom.test_regex.set_value("test_rex")
        custom.test_email.set_value("test@a.b")
        custom.test_ipv4.set_value("1.10.1.100")
        custom.test_date.set_value("2020-09-18")
        custom.test_url.set_value("https://docs.splunk.com/Documentation")
        custom.test_radio.select("No")
        custom.test_multiselect.select("Option A")
        custom.test_multiselect.select("Option B")
        assert custom.save()

    @pytest.mark.custom
    # This test case checks the validates backend save in custom tab
    def test_custom_backend_validation(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        custom.test_number.set_value("7")
        custom.test_regex.set_value("test_rex")
        custom.test_email.set_value("test@a.b")
        custom.test_ipv4.set_value("1.10.1.100")
        custom.test_date.set_value("2020-09-18")
        custom.test_url.set_value("https://docs.splunk.com/Documentation")
        custom.test_radio.select("No")
        custom.test_multiselect.select("Option A")
        custom.test_multiselect.select("Option B")
        custom.save()
        self.assert_equal(
            custom.backend_conf.get_stanza,
            {
                'disabled': False,
                'test_number': '7',
                'test_regex': 'test_rex',
                'test_string': 'test_str',
                'test_email': 'test@a.b',
                'test_ipv4': '1.10.1.100',
                'test_date': '2020-09-18',
                'test_url': 'https://docs.splunk.com/Documentation',
                'test_radio': '0',
                'test_multiselect': 'Option A|Option B'
            },
            msg="Found : {} Expected : {}".format(
                custom.backend_conf.get_stanza,
                {
                    'disabled': False,
                    'test_number': '7',
                    'test_regex': 'test_rex',
                    'test_string': 'test_str',
                    'test_email': 'test@a.b',
                    'test_ipv4': '1.10.1.100',
                    'test_date': '2020-09-18',
                    'test_url': 'https://docs.splunk.com/Documentation',
                    'test_radio': '0',
                    'test_multiselect': 'Option A|Option B'
                    }
                )
            )

    @pytest.mark.custom
    # This test case checks required field test string
    def test_custom_required_field_test_string(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        self.assert_equal(
            custom.save,
            r"Field Test String is required",
            left_args={'expect_error': True},

            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Field Test String is required"
                )
            )

    @pytest.mark.custom
    # This test case checks length of test string field should be greater than 4
    def test_custom_valid_length_test_string_greater(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test")
        self.assert_equal(
            custom.save,
            r"Length of Test String should be greater than or equal to 5",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Length of Test String should be greater than or equal to 5"
                )
            )

    @pytest.mark.custom
    # This test case checks length of test string field should be less than 11
    def test_custom_valid_length_test_string_less(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_string")
        self.assert_equal(
            custom.save,
            r"Length of Test String should be less than or equal to 10",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Length of Test String should be less than or equal to 10"
                )
            )

    @pytest.mark.custom
    # This test case checks required field test number
    def test_custom_required_field_test_number(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        self.assert_equal(
            custom.save,
            r"Field Test Number is required",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Field Test Number is required"
                )
            )

    @pytest.mark.custom
    # This test case checks test number field should be interger
    def test_custom_valid_input_test_number(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        custom.test_number.set_value("a")
        self.assert_equal(
            custom.save,
            r"Field Test Number is not a number",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Field Test Number is not a number"
                )
            )

    @pytest.mark.custom
    # This test case checks range of test number field should be between 1 to 10
    def test_custom_valid_range_test_number(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        custom.test_number.set_value("50")
        self.assert_equal(
            custom.save,
            r"Field Test Number should be within the range of [1 and 10]",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Field Test Number should be within the range of [1 and 10]"
                )
            )

    @pytest.mark.custom
    # This test case checks regex of test regex field
    def test_custom_valid_input_test_regex(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        custom.test_number.set_value("5")
        custom.test_regex.set_value("$$")
        self.assert_equal(
            custom.save,
            r"Characters of Name should match regex ^\w+$ .",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Characters of Name should match regex ^\w+$ ."
                )
            )

    @pytest.mark.custom
    # This test case checks test email field should be email
    def test_custom_valid_input_test_email(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        custom.test_number.set_value("5")
        custom.test_regex.set_value("test_rex")
        custom.test_email.set_value("abc")
        self.assert_equal(
            custom.save,
            r"Field Test Email is not a valid email address",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Field Test Email is not a valid email address"
                )
            )

    @pytest.mark.custom
    # This test case checks test ipv4 field should be valid ipv4
    def test_custom_valid_input_test_ipv4(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        custom.test_number.set_value("5")
        custom.test_regex.set_value("test_rex")
        custom.test_email.set_value("test@a.b")
        custom.test_ipv4.set_value("10.1.11")
        self.assert_equal(
            custom.save,
            r"Field Test Ipv4 is not a valid IPV4 address",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Field Test Ipv4 is not a valid IPV4 address"
                )
            )

    @pytest.mark.custom
    # This test case checks test date field should be in ISO 8601 format
    def test_custom_valid_input_test_date(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        custom.test_number.set_value("5")
        custom.test_regex.set_value("test_rex")
        custom.test_email.set_value("test@a.b")
        custom.test_ipv4.set_value("10.1.11.1")
        custom.test_date.set_value("20-10-2020")
        self.assert_equal(
            custom.save,
            r"Field Test Date is not a valid date in ISO 8601 format",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Field Test Date is not a valid date in ISO 8601 format"
                )
            )

    @pytest.mark.custom
    # This test case checks test url field should be valid url
    def test_custom_valid_input_test_url(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_string.set_value("test_str")
        custom.test_number.set_value("5")
        custom.test_regex.set_value("test_rex")
        custom.test_email.set_value("test@a.b")
        custom.test_ipv4.set_value("10.1.11.1")
        custom.test_date.set_value("2020-09-18")
        custom.test_url.set_value("\\\\")
        self.assert_equal(
            custom.save,
            r"Field Test Url is not a valid URL",
            left_args={'expect_error': True},
            msg="Found : {} Expected : {}".format(
                custom.save(expect_error=True),
                r"Field Test Url is not a valid URL"
                )
            )

    @pytest.mark.custom
    # This test case checks default value of test radio
    def test_custom_default_value_test_radio(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        self.assert_equal(
            custom.test_radio.get_value,
            r"Yes",
            msg="Found : {} Expected : {}".format(
                custom.test_radio.get_value(),
                r"Yes"
                )
            )

    @pytest.mark.custom
    # This test case checks selected value of test radio
    def test_custom_select_value_test_radio(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        custom.test_radio.select("No")
        self.assert_equal(
            custom.test_radio.get_value,
            r"No",
            msg="Found : {} Expected : {}".format(
                custom.test_radio.get_value(),
                r"No"
                )
            )

    @pytest.mark.custom
    # This test case checks values of Multiple Select Test dropdown
    def test_custom_list_test_multiselect(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        test_multiselect = ["Option A", "Option B"]
        self.assert_equal(
            list(custom.test_multiselect.list_of_values()),
            test_multiselect,
            msg="Found : {} Expected : {}".format(
                list(custom.test_multiselect.list_of_values()),
                test_multiselect
                )
            )

    @pytest.mark.custom
    # This test case checks selected single value of Multiple Select Test dropdown
    def test_custom_select_value_test_multiselect(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        selected_values = ["Option A"]
        for each in selected_values:
            custom.test_multiselect.select(each)
        self.assert_equal(
            custom.test_multiselect.get_values,
            selected_values,
            msg="Found : {} Expected : {}".format(
                custom.test_multiselect.get_values(),
                selected_values
                )
            )

    @pytest.mark.custom
    # This test case checks selected multiple values of Multiple Select Test dropdown
    def test_custom_select_multiple_values_test_multiselect(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        selected_values = ["Option A", "Option B"]
        for each in selected_values:
            custom.test_multiselect.select(each)
        self.assert_equal(
            custom.test_multiselect.get_values,
            selected_values,
            msg="Found : {} Expected : {}".format(
                custom.test_multiselect.get_values(),
                selected_values
                )
            )

    @pytest.mark.custom
    # This test case checks multiple select seach funtionality
    def test_custom_search_value_test_multiselect(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        self.assert_equal(
            custom.test_multiselect.search_get_list,
            ["Option A"],
            left_args={'value': "Option A"},
            msg="Found : {} Expected : {}".format(
                custom.test_multiselect.search_get_list("Option A"),
                ["Option A"]
                )
            )

    @pytest.mark.custom
    # This test case checks deselect funtionality of multiple select
    def test_custom_deselect_test_multiselect(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        selected_values = ["Option A", "Option B"]
        for each in selected_values:
            custom.test_multiselect.select(each)
        custom.test_multiselect.deselect("Option A")
        self.assert_equal(
            custom.test_multiselect.get_values,
            ["Option B"],
            msg="Found : {} Expected : {}".format(
                custom.test_multiselect.get_values(),
                ["Option B"]
                )
            )

    @pytest.mark.custom
    # This test case checks whether help link redirects to the correct URL
    def test_custom_help_link(self, ucc_smartx_configs):
        custom = Custom(ucc_smartx_configs)
        go_to_link = "https://docs.splunk.com/Documentation"
        self.assert_equal(
            custom.test_help_link.go_to_link,
            go_to_link,
            msg="Found : {} Expected : {}".format(
                custom.test_help_link.go_to_link(),
                go_to_link
                )
            )