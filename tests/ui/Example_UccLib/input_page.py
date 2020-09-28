
from .Base_UccLib.pages.page import Page
from .Base_UccLib.components.tabs import Tab
from .Base_UccLib.components.dropdown import Dropdown
from .Base_UccLib.components.entity import Entity
from .Base_UccLib.components.controls.button import Button
from .Base_UccLib.components.controls.checkbox import Checkbox
from .Base_UccLib.components.controls.learn_more import LearnMore
from .Base_UccLib.components.controls.textbox import TextBox
from .Base_UccLib.components.controls.single_select import SingleSelect
from .Base_UccLib.components.controls.multi_select import MultiSelect
from .Base_UccLib.components.input_table import InputTable
from .Base_UccLib.backend_confs import ListBackendConf
from .Base_UccLib.components.controls.toggle import Toggle
from selenium.webdriver.common.by import By

class ExampleInputOne(Entity):
    """
    Form to configure a new Input
    """
    def __init__(self, browser, container):
        """
            :param browser: The selenium webdriver
            :param container: The container in which the entity is located in
        """
        add_btn = Button(browser, {"by": By.CSS_SELECTOR, "select": container["select"] + " .add-button" })
        entity_container = {"by": By.CSS_SELECTOR, "select": ".modal-content"}
        
        super(ExampleInputOne, self).__init__(browser, entity_container, add_btn=add_btn, wait_for=10)

        # Controls
        self.name = TextBox(browser, {"by": By.NAME, "select": "name"})
        self.example_checkbox = Checkbox(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .input_one_checkbox"})
        self.example_radio = Toggle(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .input_one_radio"})
        self.single_select_group_test = SingleSelect(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .singleSelectTest"})
        self.multiple_select_test = MultiSelect(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .multipleSelectTest"})
        self.interval = TextBox(browser, {"by": By.NAME, "select": "interval"})
        self.index = SingleSelect(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .index"})
        self.example_account = SingleSelect(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .account"})
        self.object = TextBox(browser, {"by": By.NAME, "select": "object"})
        self.object_fields = TextBox(browser, {"by": By.NAME, "select": "object_fields"})
        self.order_by = TextBox(browser, {"by": By.NAME, "select": "order_by"})
        self.query_start_date = TextBox(browser, {"by": By.NAME, "select": "start_date"})
        self.limit = TextBox(browser, {"by": By.NAME, "select": "limit"})
        self.help_link = LearnMore(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .example_help_link a"})

class ExampleInputTwo(Entity):
    """
    Form to configure a new Input
    """
    def __init__(self, browser, container):
        """
            :param browser: The selenium webdriver
            :param container: The container in which the entity is located in
        """
        add_btn = Button(browser, {"by": By.CSS_SELECTOR, "select": container["select"] + " .add-button" })
        entity_container = {"by": By.CSS_SELECTOR, "select": ".modal-content"}
        
        super(ExampleInputTwo, self).__init__(browser, entity_container, add_btn=add_btn, wait_for=10)

        # Controls
        self.name = TextBox(browser, {"by": By.NAME, "select": "name"})
        self.interval = TextBox(browser, {"by": By.NAME, "select": "interval"})
        self.index = SingleSelect(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .index"})
        self.example_account = SingleSelect(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .account"})
        self.example_multiple_select = MultiSelect(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .input_two_multiple_select"})
        self.example_checkbox = Checkbox(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .input_two_checkbox"})
        self.example_radio = Toggle(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .input_two_radio"})
        self.query_start_date = TextBox(browser, {"by": By.NAME, "select": "start_date"})
        self.help_link = LearnMore(browser, {"by": By.CSS_SELECTOR, "select": entity_container["select"] + " .example_help_link a"})
    
class InputPage(Page):
    """
    Page: Input page
    """

    def __init__(self, browser, urls, session_key):
        """
            :param browser: The selenium webdriver
            :param urls: Splunk web & management url. {"web": , "mgmt": }
            :param session_key: session key to access the rest endpoints
        """
        super(InputPage, self).__init__(browser, urls)

        input_container = {
            "by": By.CSS_SELECTOR,
            "select": "div.inputsContainer"
        }
        
        self.create_new_input = Dropdown(browser, {"by": By.CSS_SELECTOR, "select": ".add-button"})
        self.table = InputTable(browser, input_container, mapping={"status": "disabled", "input_type":3})
        self.entity1 = ExampleInputOne(browser, input_container)
        self.entity2 = ExampleInputTwo(browser, input_container)
        self.backend_conf = ListBackendConf(self._get_input_endpoint(), session_key)
        self.pagination = Dropdown(browser, {"by": By.CSS_SELECTOR, "select": "control btn-group shared-controls-syntheticselectcontrol control-default"})
        self.type_filter = Dropdown(browser, {"by": By.CSS_SELECTOR, "select": " .type-filter"})

    def open(self):
        self.browser.get('{}/en-US/app/Splunk_TA_UCCExample/inputs'.format(self.splunk_web_url))

    def _get_input_endpoint(self):
        return '{}/servicesNS/nobody/Splunk_TA_UCCExample/configs/conf-inputs'.format(self.splunk_mgmt_url)

