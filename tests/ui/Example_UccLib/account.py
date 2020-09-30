from ucc_smartx.pages.page import Page
from ucc_smartx.components.tabs import Tab
from ucc_smartx.components.entity import Entity
from ucc_smartx.components.controls.button import Button
from ucc_smartx.components.controls.single_select import SingleSelect
from ucc_smartx.components.controls.oauth_select import OAuthSelect
from ucc_smartx.components.controls.multi_select import MultiSelect
from ucc_smartx.components.controls.checkbox import Checkbox
from ucc_smartx.components.controls.toggle import Toggle
from ucc_smartx.components.controls.textbox import TextBox
from ucc_smartx.components.controls.learn_more import LearnMore
from ucc_smartx.components.controls.toggle import Toggle
from ucc_smartx.components.conf_table import ConfigurationTable
from ucc_smartx.backend_confs import ListBackendConf
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
        add_btn = Button(browser, {"by": By.CSS_SELECTOR, "select": container["select"] + " button.add-button" })
        entity_container = {"by": By.CSS_SELECTOR, "select": ".modal-content"}
        
        super(AccountEntity, self).__init__(browser, entity_container, add_btn=add_btn)

        # Controls
        self.name = TextBox(browser, {"by": By.NAME, "select": "name"})
        self.environment = SingleSelect(browser, {"by": By.CSS_SELECTOR, "select": ".custom_endpoint"}, False)
        self.account_radio = Toggle(browser, {"by": By.CSS_SELECTOR, "select": ".account_radio"})
        self.example_checkbox = Checkbox(browser, {"by": By.CSS_SELECTOR, "select": ".account_checkbox"})
        self.multiple_select = MultiSelect(browser, {"by": By.CSS_SELECTOR, "select": ".account_multiple_select"})
        self.auth_key = OAuthSelect(browser, {"by": By.CSS_SELECTOR, "select": ".auth_type"})
        self.username = TextBox(browser, {"by": By.CSS_SELECTOR, "select": ".shared-controls-textcontrol .username"})
        self.password = TextBox(browser, {"by": By.CSS_SELECTOR, "select": ".shared-controls-textcontrol .password"})
        self.security_token = TextBox(browser, {"by": By.CSS_SELECTOR, "select": ".shared-controls-textcontrol .token"})
        self.client_id = TextBox(browser, {"by": By.CSS_SELECTOR, "select": ".shared-controls-textcontrol .client_id"})
        self.client_secret = TextBox(browser, {"by": By.CSS_SELECTOR, "select": ".shared-controls-textcontrol .client_secret"})
        self.redirect_url = TextBox(browser, {"by": By.CSS_SELECTOR, "select": ".shared-controls-textcontrol .redirect_url"})
        self.search_query  = TextBox(browser, {"by": By.CSS_SELECTOR, "select": " .search-query"})
        self.help_link = LearnMore(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .example_help_link a"})
        
class AccountPage(Page):
    """
    Page: Server page
    """
    def __init__(self, ucc_smartx_configs):
        """
            :param ucc_smartx_configs: smartx configuration fixture
        """
        super(AccountPage, self).__init__(ucc_smartx_configs)
        account_container = {
            "by": By.CSS_SELECTOR,
            "select": "div#account-tab"
        }
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