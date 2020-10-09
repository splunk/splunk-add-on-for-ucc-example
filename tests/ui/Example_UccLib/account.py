from pytest_splunk_addon_ui_smartx.pages.page import Page
from pytest_splunk_addon_ui_smartx.components.base_component import Selector
from pytest_splunk_addon_ui_smartx.components.base_component import BaseComponent
from pytest_splunk_addon_ui_smartx.components.tabs import Tab
from pytest_splunk_addon_ui_smartx.components.entity import Entity
from pytest_splunk_addon_ui_smartx.components.controls.button import Button
from pytest_splunk_addon_ui_smartx.components.controls.single_select import SingleSelect
from pytest_splunk_addon_ui_smartx.components.controls.oauth_select import OAuthSelect
from pytest_splunk_addon_ui_smartx.components.controls.multi_select import MultiSelect
from pytest_splunk_addon_ui_smartx.components.controls.checkbox import Checkbox
from pytest_splunk_addon_ui_smartx.components.controls.toggle import Toggle
from pytest_splunk_addon_ui_smartx.components.controls.textbox import TextBox
from pytest_splunk_addon_ui_smartx.components.controls.learn_more import LearnMore
from pytest_splunk_addon_ui_smartx.components.controls.toggle import Toggle
from pytest_splunk_addon_ui_smartx.components.controls.message import Message
from pytest_splunk_addon_ui_smartx.components.conf_table import ConfigurationTable
from pytest_splunk_addon_ui_smartx.backend_confs import ListBackendConf
from selenium.webdriver.common.by import By

class AccountEntity(Entity):
    """
    Form to configure a new Server
    """
    def __init__(self, browser, container):
        """
            :param browser: The selenium webdriver
            :param container: The container in which the entity is located in
        """
        add_btn = Button(browser, Selector(select=container.select + " button.add-button" ))
        entity_container = Selector(select=".modal-content")
        
        super(AccountEntity, self).__init__(browser, entity_container, add_btn=add_btn)

        # Controls
        self.name = TextBox(browser, Selector(select=".name"))
        self.environment = SingleSelect(browser, Selector(select=".custom_endpoint"), False)
        self.account_radio = Toggle(browser, Selector(select=".account_radio"))
        self.example_checkbox = Checkbox(browser, Selector(select=".account_checkbox"))
        self.multiple_select = MultiSelect(browser, Selector(select=".account_multiple_select"))
        self.auth_key = OAuthSelect(browser, Selector(select=".auth_type"))
        self.username = TextBox(browser, Selector(select=".shared-controls-textcontrol .username"))
        self.password = TextBox(browser, Selector(select=".shared-controls-textcontrol .password"))
        self.security_token = TextBox(browser, Selector(select=".shared-controls-textcontrol .token"))
        self.client_id = TextBox(browser, Selector(select=".shared-controls-textcontrol .client_id"))
        self.client_secret = TextBox(browser, Selector(select=".shared-controls-textcontrol .client_secret"))
        self.redirect_url = TextBox(browser, Selector(select=".shared-controls-textcontrol .redirect_url"))
        self.search_query  = TextBox(browser, Selector(select=" .search-query"))
        self.help_link = LearnMore(browser, Selector(select=entity_container.select + " .example_help_link a"))
        self.title = BaseComponent(browser, Selector(select= "h4.modal-title"))
        
class AccountPage(Page):
    """
    Page: Server page
    """
    def __init__(self, ucc_smartx_configs):
        """
            :param ucc_smartx_configs: smartx configuration fixture
        """
        super(AccountPage, self).__init__(ucc_smartx_configs)
        account_container = Selector(select="div#account-tab")
        self.title = Message(ucc_smartx_configs.browser, Selector(by=By.CLASS_NAME, select="tool-title"))
        self.description = Message(ucc_smartx_configs.browser, Selector(by=By.CLASS_NAME, select="tool-description"))
        self.table = ConfigurationTable(ucc_smartx_configs.browser, account_container)
        self.entity = AccountEntity(ucc_smartx_configs.browser, account_container)
        self.backend_conf = ListBackendConf(self._get_account_endpoint(), ucc_smartx_configs.session_key)

    def open(self):
        """
        Open the required page. Page(super) class opens the page by default.
        """

        self.browser.get('{}/en-US/app/Splunk_TA_UCCExample/configuration'.format(self.splunk_web_url))
        tab = Tab(self.browser)
        tab.open_tab("account")

    def _get_account_endpoint(self):
        """
        Get rest endpoint for the configuration
        """
        return '{}/servicesNS/nobody/Splunk_TA_UCCExample/configs/conf-splunk_ta_uccexample_account'.format(self.splunk_mgmt_url)