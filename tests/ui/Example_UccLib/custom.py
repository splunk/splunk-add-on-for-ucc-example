
from pytest_splunk_addon_ui_smartx.components.base_component import Selector
from pytest_splunk_addon_ui_smartx.components.tabs import Tab
from pytest_splunk_addon_ui_smartx.components.entity import Entity
from pytest_splunk_addon_ui_smartx.components.controls.textbox import TextBox
from pytest_splunk_addon_ui_smartx.components.controls.toggle import Toggle
from pytest_splunk_addon_ui_smartx.components.controls.multi_select import MultiSelect
from pytest_splunk_addon_ui_smartx.components.controls.learn_more import LearnMore
from pytest_splunk_addon_ui_smartx.backend_confs import SingleBackendConf
from selenium.webdriver.common.by import By
import time


class Custom(Entity):

    def __init__(self, ucc_smartx_configs):
        """
            :param ucc_smartx_configs: fixture contains browser, urls and session key
        """
        entity_container = Selector(select="#customized-tab-tab")
        super(Custom, self).__init__(ucc_smartx_configs.browser, entity_container)
        self.splunk_web_url = ucc_smartx_configs.splunk_web_url
        self.splunk_mgmt_url = ucc_smartx_configs.splunk_mgmt_url
        self.open()

        # Components
        self.test_string = TextBox(ucc_smartx_configs.browser, Selector(by=By.NAME, select="test_string"))
        self.test_number = TextBox(ucc_smartx_configs.browser, Selector(by=By.NAME, select="test_number"))
        self.test_regex = TextBox(ucc_smartx_configs.browser, Selector(by=By.NAME, select="test_regex"))
        self.test_email = TextBox(ucc_smartx_configs.browser, Selector(by=By.NAME, select="test_email"))
        self.test_ipv4 = TextBox(ucc_smartx_configs.browser, Selector(by=By.NAME, select="test_ipv4"))
        self.test_date = TextBox(ucc_smartx_configs.browser, Selector(by=By.NAME, select="test_date"))
        self.test_url = TextBox(ucc_smartx_configs.browser, Selector(by=By.NAME, select="test_url"))
        self.test_radio = Toggle(ucc_smartx_configs.browser, Selector(select=".test_radio"))
        self.test_multiselect = MultiSelect(ucc_smartx_configs.browser, Selector(select=".test_multiselect"))
        self.test_help_link = LearnMore(ucc_smartx_configs.browser, Selector(select=".test_help_link a"))
        self.backend_conf = SingleBackendConf(self._get_custom_url(), ucc_smartx_configs.session_key)

    def open(self):
        """
        Open the required page. Page(super) class opens the page by default.
        """
        self.browser.get(
            '{}/en-US/app/Splunk_TA_UCCExample/configuration'.format(self.splunk_web_url))
        tab = Tab(self.browser)
        tab.open_tab("customized-tab")

    def _get_custom_url(self):
        """
        get rest endpoint for the configuration
        """
        return '{}/servicesNS/nobody/Splunk_TA_UCCExample/configs/conf-splunk_ta_uccexample_settings/custom_tab'.format(self.splunk_mgmt_url)
