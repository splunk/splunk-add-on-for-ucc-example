import pytest
import logging
import traceback
logger = logging.getLogger(__name__)

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """
    pytest_runtest_makereport will be called after each test case is executed.
    Capture a screenshot if the test case is failed.
    item.selenium_helper has been added by the fixture "test_helper". The scope of the fixture must be function.
        :param item: the method of the test case.
    """
    logger.debug("pytest_runtest_makereport: Start making report")
    try:
        pytest_html = item.config.pluginmanager.getplugin('html')
        logger.debug("pytest_runtest_makereport: pytest_html init")
        if pytest_html:
            outcome = yield
            report = outcome.get_result()
            if report.when == "call":
                setattr(item, 'report', report)
                if report.failed:
                    logger.debug("pytest_runtest_makereport: test_case failed")
                    try:
                        screenshot_path = item.nodeid.split("::")[-1] + ".png"
                        logger.debug("pytest_runtest_makereport: screenshot_path={}".format(screenshot_path))
                        item.selenium_helper.browser.save_screenshot(screenshot_path)
                        report.extra = [pytest_html.extras.image(screenshot_path)]
                        logger.debug("pytest_runtest_makereport: image_added to the report")
                    except:
                        logger.warn("Screenshot can not be captured. Scope of the fixture test_helper must be 'function' to capture the screenshot. ")
        else:
            logger.warn("pytest-html is not installed. Install by using: pip install pytest-html")
    except Exception as e:
        logger.warn("Got exception while making test report. Exception  {}".format(e))
        logger.debug("test_report, Exception: {}".format(traceback.format_exc()))

def pytest_addoption(parser):
    """
    Add options to the pytest. The options are used at base_test.py in the framework.
    """
    parser.addoption(
        "--browser", action="store", help="browser on which the test should run. supported_values: (firefox, chrome, IE)"
    )
    parser.addoption(
        "--local", action="store_true", help="The test will be run on local browsers"
    )

    parser.addoption(
        "--web_url", action="store", help="Splunk web url"
    )

    parser.addoption(
        "--mgmt_url", action="store", help="Splunk management port url"
    )

    parser.addoption(
        "--user", action="store", help="Splunk instance username"
    )

    parser.addoption(
        "--password", action="store", help="Splunk instance account password"
    )