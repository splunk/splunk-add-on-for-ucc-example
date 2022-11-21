"""
Meta
====
    $Id$  # nopep8
    $DateTime$
    $Author$
    $Change$
"""
import logging
import pytest
import os
import sys
import base64

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "centaurs"))
from splunktatest.BaseTATest import BaseTATest
from pytest_splunk_addon.helmut.splunk.cloud import CloudSplunk
from .O365TATest import O365TATest
from .data_generator import AuditADGen, AuditSharepointGen, AuditExchangeGen
from random import randint

logging.basicConfig(filename="conftest.log", level=logging.DEBUG)
LOGGER = logging.getLogger()

DEFAULT_ORCA_HOST = "so1"
DEFAULT_ORCA_SSH_PORT = 2222
DEFAULT_ORCA_PASSWORD = "Chang3d!"
DEFAULT_ORCA_SPLUNK_HOME = "/opt/splunk"

# Data Gen related constants
DOMAIN = "splunkcdcdev.onmicrosoft.com"
RANDOM_INT = str(randint(0, 10000000))
USER_DETAILS = {
    "accountEnabled": True,
    "city": "Seattle",
    "country": "United States",
    "department": "Department",
    "displayName": "ModInput User_{}".format(RANDOM_INT),
    "givenName": "ModInput",
    "jobTitle": "Software Engineer",
    "mailNickname": "modinput_{}".format(RANDOM_INT),
    "passwordPolicies": "DisablePasswordExpiration",
    "passwordProfile": {
        "password": "12abc34d-e1f4-0575-603c-bce789eef3d6",
        "forceChangePasswordNextSignIn": False,
    },
    "officeLocation": "100/1100",
    "postalCode": "12345",
    "preferredLanguage": "en-US",
    "state": "WA",
    "streetAddress": "1234 ABC 200",
    "surname": "Darrow",
    "mobilePhone": "+1 123 555 4567",
    "usageLocation": "US",
    "userPrincipalName": "modinput_{}@{}".format(RANDOM_INT, DOMAIN),
}
LIST_DETAILS = {
    "displayName": "TestCases_{}".format(RANDOM_INT),
    "columns": [{"name": "ModInput", "text": {}}, {"name": "Unit", "number": {}}],
    "list": {"template": "genericList"},
}
GROUP_DETAILS = {
    "description": "Created group as part of data generation for test cases",
    "displayName": "ModInputDataGenGroup_{}".format(RANDOM_INT),
    "groupTypes": ["Unified"],
    "mailEnabled": True,
    "mailNickname": "modinput_data_gen_{}".format(RANDOM_INT),
    "securityEnabled": False,
}

LOGGER.info("IN CONFTEST")


def pytest_generate_tests(metafunc):
    for funcargs in getattr(metafunc.function, "funcarglist", ()):
        if "testname" in funcargs:
            testname = "%s" % funcargs["testname"]
            metafunc.addcall(funcargs=funcargs, id=testname)
        else:
            metafunc.addcall(funcargs=funcargs)


@pytest.fixture(scope="function")
def audit_ad_gen():
    """
    Generate events for workload: AzureActiveDirectory
    Create/Add user and delete user
    """

    # DataGenerator to initialize tenantid, clientid, clientseceret
    # and get access token
    audit_ad_data_generator = AuditADGen(
        O365TATest.DATA_GEN_TENANT_ID,
        O365TATest.DATA_GEN_CLIENT_ID,
        O365TATest.DATA_GEN_CLIENT_SECRET,
    )

    # create user
    response = audit_ad_data_generator.create_user(USER_DETAILS)
    user_id = response["id"]

    # delete user
    audit_ad_data_generator.delete_user(user_id)


@pytest.fixture(scope="function")
def audit_sharepoint_gen():
    """
    Generate events for workload: SharePoint
    Create List and Delete List
    """

    audit_sharepoint_data_generator = AuditSharepointGen(
        O365TATest.DATA_GEN_TENANT_ID,
        O365TATest.DATA_GEN_CLIENT_ID,
        O365TATest.DATA_GEN_CLIENT_SECRET,
    )

    # get site id
    response = audit_sharepoint_data_generator.get_site()
    site_id = response["id"].split(",")

    # create list in site
    response = audit_sharepoint_data_generator.create_list(site_id[1], LIST_DETAILS)

    # delete list from site
    audit_sharepoint_data_generator.delete_list(site_id[1], LIST_DETAILS["displayName"])


@pytest.fixture(scope="function")
def audit_exchange_gen():
    """
    Generate events for workload: Exchange
    Create Group and Delete Group
    """

    audit_exchange_data_generator = AuditExchangeGen(
        O365TATest.DATA_GEN_TENANT_ID,
        O365TATest.DATA_GEN_CLIENT_ID,
        O365TATest.DATA_GEN_CLIENT_SECRET,
    )

    # create group
    response = audit_exchange_data_generator.create_group(GROUP_DETAILS)
    group_id = response["id"]

    # delete group
    audit_exchange_data_generator.delete_group(group_id)


def params(funcarglist):
    """
    Method used with generated/parameterized tests, can be used to decorate
    your test function with the parameters.  Each dict in your list
    represents on generated test.  The keys in that dict are the parameters
    to be used for that generated test
    """

    def wrapper(function):
        """
        Wrapper function to add the funcarglist to the function
        """
        function.funcarglist = funcarglist
        return function

    return wrapper


def pytest_addoption(parser):
    """
    Adds extra command line arguments to py.test
    """
    """
    This is a pytest hook to add options from the command line so that
    we can use it later.
    """
    splk_group = parser.getgroup("Splunk Options")
    splk_group.addoption(
        "--splunk-url",
        dest="splunk_url",
        help="The url of splunk instance",
        default="so1",
    )
    splk_group.addoption(
        "--remote",
        dest="remote",
        action="store_true",
        help="Whether this is a remote test",
        default=False,
    )
    splk_group.addoption(
        "--ssh_username", dest="ssh_username", help="remote ssh username", default=""
    )
    splk_group.addoption(
        "--ssh_password", dest="ssh_password", help="remote ssh password", default=""
    )
    splk_group.addoption(
        "--ssh_port", dest="ssh_port", help="remote ssh port", default=""
    )
    splk_group.addoption(
        "--orca",
        dest="orca",
        action="store_true",
        help="Whether this is a orca test",
        default=False,
    )
    splk_group.addoption(
        "--username",
        dest="username",
        help="Splunk username, defaults to admin",
        default="admin",
    )
    splk_group.addoption(
        "--password",
        dest="password",
        help="Splunk password, defaults to Chang3d!",
        default="Chang3d!",
    )
    splk_group.addoption(
        "--splunkd-port",
        dest="splunkd_port",
        help="Splunk Management port, defaults to 8089",
        default="8089",
    )
    splk_group.addoption(
        "--splunk-home",
        dest="splunk_home",
        help="The location of the Splunk instance, if using a "
        "pre-installed splunk instance",
        default="/opt/splunk",
    )

    splk_group.addoption(
        "--client_id",
        dest="client_id",
        help="the client id which is automatically generated when registering with Azure AD",
    )
    splk_group.addoption(
        "--client_secret",
        dest="client_secret",
        help="the password for client_id",
    )
    splk_group.addoption(
        "--tenant_id",
        dest="tenant_id",
        help="The UUID which point to the AD containing your application",
    )

    splk_group.addoption(
        "--data_gen_client_id",
        dest="data_gen_client_id",
        help="The client id which is automatically generated when registering with Azure AD for data generation",
    )
    splk_group.addoption(
        "--data_gen_client_secret",
        dest="data_gen_client_secret",
        help="The password for data_gen_client_id",
    )
    splk_group.addoption(
        "--data_gen_tenant_id",
        dest="data_gen_tenant_id",
        help="The UUID which point to the AD containing your application for data generation",
    )

    splk_group.addoption(
        "--proxy_host",
        dest="proxy_host",
        help="the host of proxy to connect",
    )
    splk_group.addoption(
        "--proxy_port",
        dest="proxy_port",
        help="the port of proxy to connect",
        default=3128,
    )
    splk_group.addoption(
        "--proxy_username",
        dest="proxy_username",
        help="username for proxy",
    )
    splk_group.addoption(
        "--proxy_password",
        dest="proxy_password",
        help="The UUID which point to the AD containing your application",
    )
    splk_group.addoption(
        "--enterprise-cloud",
        dest="enterprise_cloud",
        action="store_true",
        help="Provide the param if the tests are executed on enterprise_cloud",
        default=False,
    )


def pytest_configure(config):
    """
    Handles pytest configuration, runs before the session start.
    Initialize the parameters required by Centaurs and test cases.
    """
    BaseTATest.username = config.getvalue("username")
    BaseTATest.password = config.getvalue("password")
    BaseTATest.splunk_url = config.getvalue("splunk_url")
    BaseTATest.splunk_home = config.getvalue("splunk_home")
    BaseTATest.remote = config.getvalue("remote")
    BaseTATest.orca = config.getvalue("orca")
    O365TATest.CLIENT_ID = (
        config.getvalue("client_id")
        or base64.b64decode(os.environ["CLIENT_ID"]).decode().strip()
    )
    O365TATest.CLIENT_SECRET = (
        config.getvalue("client_secret")
        or base64.b64decode(os.environ["CLIENT_SECRET"]).decode().strip()
    )
    O365TATest.TENANT_ID = (
        config.getvalue("tenant_id")
        or base64.b64decode(os.environ["TENANT_ID"]).decode().strip()
    )
    O365TATest.DATA_GEN_CLIENT_ID = (
        config.getvalue("data_gen_client_id")
        or base64.b64decode(os.environ["DATA_GEN_CLIENT_ID"]).decode().strip()
    )
    O365TATest.DATA_GEN_CLIENT_SECRET = (
        config.getvalue("data_gen_client_secret")
        or base64.b64decode(os.environ["DATA_GEN_CLIENT_SECRET"]).decode().strip()
    )
    O365TATest.DATA_GEN_TENANT_ID = (
        config.getvalue("data_gen_tenant_id")
        or base64.b64decode(os.environ["DATA_GEN_TENANT_ID"]).decode().strip()
    )
    O365TATest.PROXY_HOST = (
        config.getvalue("proxy_host")
        or base64.b64decode(os.environ["HTTP_HOST"]).decode().strip()
    )
    O365TATest.PROXY_PORT = config.getvalue("proxy_port")
    O365TATest.PROXY_PASSWORD = (
        config.getvalue("proxy_password")
        or base64.b64decode(os.environ["HTTP_PASSWORD"]).decode().strip()
    )
    O365TATest.PROXY_USERNAME = (
        config.getvalue("proxy_username")
        or base64.b64decode(os.environ["HTTP_USERNAME"]).decode().strip()
    )

    if config.getvalue("remote"):
        O365TATest.enterprise_cloud = config.getvalue("enterprise_cloud")
        ssh_conn = CloudSplunk(
            splunkd_host=config.getvalue("splunk_url"),
            splunkd_port=config.getvalue("splunkd_port"),
            username=config.getvalue("username"),
            password=config.getvalue("password"),
        )
        LOGGER.info("This is a remote test. Linux/Mac")
        BaseTATest.splunk = ssh_conn

    elif config.getvalue("orca"):
        splunk_conn = CloudSplunk(
            splunkd_host=config.getvalue("splunk_url"),
            splunkd_port=config.getvalue("splunkd_port"),
            username=config.getvalue("username"),
            password=config.getvalue("password"),
        )
        BaseTATest.password = DEFAULT_ORCA_PASSWORD
        BaseTATest.splunk_url = DEFAULT_ORCA_HOST
        BaseTATest.splunk_home = DEFAULT_ORCA_SPLUNK_HOME
        BaseTATest.splunk = splunk_conn
        BaseTATest.remote = True
    BaseTATest.splunk.set_credentials_to_use(
        username=BaseTATest.username, password=BaseTATest.password
    )
