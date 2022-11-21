import os
import json
import base64
import random
import pytest
import umsgpack
import requests

try:
    basestring
except NameError:
    basestring = str

from splunktatest.BaseTATest import BaseTATest
from pytest_splunk_addon.helmut.util import rip
import requests
import time


class O365TATest(BaseTATest):
    # due to the pytest frame, we can not add __init__ function in this class
    # self.account_set is used to store the accounts which are created

    TA_APP_NAME = "splunk_ta_o365"
    TA_APP_USER = "nobody"
    CLIENT_ID = None
    TENANT_ID = None
    CLIENT_SECRET = None
    PROXY_HOST = None
    PROXY_PORT = None
    PROXY_USERNAME = None
    PROXY_PASSWORD = None
    # SLEEP_TIME: Max time for test case to complete execution including retries,
    # If any test case is getting failed due to event getting delayed from API, increase the value of SLEEP_TIME
    SLEEP_TIME = 300
    # RETRY_INTERVAL: It would check for event in Splunk using search query at every RETRY_INTERVAL seconds
    # until SLEEP_TIME is reached
    RETRY_INTERVAL = 10
    CKP_FILEPATH_SERVICE_STATUS = (
        "var/lib/splunk/modinputs/splunk_ta_o365_service_status/"
    )
    CKP_FILEPATH_MANAGEMENT_ACTIVITY = (
        "var/lib/splunk/modinputs/splunk_ta_o365_management_activity/"
    )
    CKP_FILEPATH_SERVICE_MESSAGE = (
        "var/lib/splunk/modinputs/splunk_ta_o365_service_message/"
    )
    enterprise_cloud = None
    enterprise_cloud_index_endpoint = "/servicesNS/nobody/000-self-service/cluster_blaster_indexes/sh_indexes_manager/"

    @classmethod
    def setup_class(cls):
        super(O365TATest, cls).setup_class()
        cls.logger.info("Starting setup methods...")
        cls.register_rest_api()
        cls.logger.info(
            "Test Begins. TA build under test is %s", O365TATest.get_ta_build_number()
        )
        cls.create_office_azure_accounts()

    @classmethod
    def teardown_class(cls):
        super(O365TATest, cls).teardown_class()
        cls.delete_office_azure_accounts("tenant_worldwide")

    def setup_method(self, method):
        super(O365TATest, self).setup_method(method)
        self.remove_checkpoints = []

    def teardown_method(self, method):
        super(O365TATest, self).teardown_method(method)
        for remove_checkpoint_dict in self.remove_checkpoints:
            task_type = remove_checkpoint_dict["task_type"]
            task_name = remove_checkpoint_dict["task_name"]
            ckp_file = task_name + ".ckpt"
            lock_file = task_name + ".lock"
            remove_chk_dict = {task_type: [ckp_file, lock_file]}
            self.remove_checkpoint(remove_chk_dict)
        if hasattr(self, "remove_ckpt_tr"):
            self.remove_checkpoint_from_test_runner(self.remove_ckpt_tr)
        if hasattr(self, "delete_task"):
            task_dict = self.delete_task
            if task_dict["task_type"] == "MANAGEMENT_ACTIVITY":
                self.delete_management_activity_task(task_dict["task_name"])
            if task_dict["task_type"] == "SERVICE_STATUS":
                self.delete_service_status_task(task_dict["task_name"])
            if task_dict["task_type"] == "SERVICE_MESSAGE":
                self.delete_service_message_task(task_dict["task_name"])

    @classmethod
    def register_rest_api(cls):
        """
        Update REST API for O365 TA
        """
        rip.RESTInPeace.URIS.update(
            {
                "azure_account": "/servicesNS/{u}/{a}/configs/conf-splunk_ta_o365_tenants",
                "secret": "/servicesNS/{u}/{a}/storage/passwords",
                "office_settings": "/servicesNS/{u}/{a}/configs/conf-splunk_ta_o365_settings",
                "splunk_ta_o365_graph_api": "/servicesNS/{u}/{a}/data/inputs/splunk_ta_o365_graph_api",
                "management_activity_input": "/servicesNS/{u}/{a}/data/inputs/splunk_ta_o365_management_activity",
                "service_status_input": "/servicesNS/{u}/{a}/data/inputs/splunk_ta_o365_service_status",
                "service_message_input": "/servicesNS/{u}/{a}/data/inputs/splunk_ta_o365_service_message",
                "checkpoint_input": "/servicesNS/{u}/Splunk_TA_Modinput_Test/Splunk_TA_Modinput_Test_perform_crd_operation/<entry>",
            }
        )
        cls.rest.change_namespace(cls.TA_APP_USER, cls.TA_APP_NAME)

    @classmethod
    def create_office_azure_accounts(cls):
        """
        Creates tenant using splunk_ta_o365_tenants.conf
        """
        configs = cls.get_azure_accounts_configuration()
        # Store client_secret on password endpoint
        secret_key_name = cls.get_secret_key_name(str(configs["name"]), "client_secret")
        secret_config = {"name": secret_key_name, "password": cls.CLIENT_SECRET}
        cls.rest.create_secret(**secret_config)
        cls.rest.wait_for_secret_to_be_created(secret_config["name"], timeout=3)

        cls.logger.info("Create tenant with config %s", configs)
        # Create tenant
        cls.rest.create_azure_account(**configs)
        cls.rest.wait_for_azure_account_to_be_created(configs["name"], timeout=3)

    @classmethod
    def delete_office_azure_accounts(cls, account_name=None):
        """
        Deletes tenant for given account name
        :param account_name: name of the account to be deleted
        """
        cls.logger.info("Delete tenant %s", account_name)
        cls.rest.delete_azure_account(account_name)

    @classmethod
    def get_azure_accounts_configuration(cls):
        """
        Get the configuration for tenant from splunk_ta_o365_tenants.conf
        :return configuration for creating tenant
        """
        account_id = "tenant_worldwide"

        configs = {
            "name": account_id,
            "client_id": cls.CLIENT_ID,
            "client_secret": "********",
            "tenant_id": cls.TENANT_ID,
            "endpoint": "Worldwide",
        }
        return configs

    def get_config(self, task_name, index_name, content_type=None):
        """
        Give the configuration to create input
        :param task_name: name of the input
        :param index_name: name of the index to ingest data
        :param content_type: type of content for the input
        :return dict with input configuration
        """
        config = {
            "name": task_name,
            "tenant_name": "tenant_worldwide",
            "index": index_name,
            "interval": "60",
        }
        if content_type:
            config["content_type"] = content_type

        return config

    def create_management_activity_task(self, configs):
        """
        Create a management activity input with config parsed in
        param configs: The dict of management activity input config
        """
        self.logger.info("Create management activity input with config %s", configs)
        self.rest.create_management_activity_input(**configs)
        self.rest.wait_for_management_activity_input_to_be_created(
            configs["name"], timeout=120
        )

    def delete_management_activity_task(self, input_name):
        """
        Deletes management activity input for given input name
        :param input_name: name of the input to be deleted
        """
        self.rest.delete_management_activity_input(input_name)
        self.rest.wait_for_management_activity_input_to_be_deleted(
            input_name, timeout=3
        )

    def create_splunk_ta_o365_graph_api_task(self, configs):
        """
        Create a management activity input with config parsed in
        param configs: The dict of management activity input config
        """
        self.logger.info("Create GRAPH API input with config %s", configs)
        self.rest.create_splunk_ta_o365_graph_api(**configs)
        self.rest.wait_for_splunk_ta_o365_graph_api_to_be_created(
            configs["name"], timeout=120
        )

    def delete_splunk_ta_o365_graph_api_task(self, input_name):
        """
        Deletes management activity input for given input name
        :param input_name: name of the input to be deleted
        """
        self.rest.delete_splunk_ta_o365_graph_api(input_name)
        self.rest.wait_for_splunk_ta_o365_graph_api_to_be_deleted(input_name, timeout=3)

    def create_service_status_task(self, configs):
        """
        Create a service status input with config parsed in
        param configs: The dict of service status input config
        """
        self.logger.info("Create service status input with config %s", configs)
        self.rest.create_service_status_input(**configs)
        self.rest.wait_for_service_status_input_to_be_created(
            configs["name"], timeout=3
        )

    def delete_service_status_task(self, input_name):
        """
        Deletes service status input for given input name
        :param input_name: name of the input to be deleted
        """
        self.rest.delete_service_status_input(input_name)
        self.rest.wait_for_service_status_input_to_be_deleted(input_name, timeout=3)

    def create_service_message_task(self, configs):
        """
        Create a service message input with config parsed in
        param configs: The dict of service message input config
        """
        self.logger.info("Create service message input with config %s", configs)
        self.rest.create_service_message_input(**configs)
        self.rest.wait_for_service_message_input_to_be_created(
            configs["name"], timeout=3
        )

    def delete_service_message_task(self, input_name):
        """
        Deletes service message input for given input name
        :param input_name: name of the input to be deleted
        """
        self.rest.delete_service_message_input(input_name)
        self.rest.wait_for_service_message_input_to_be_deleted(input_name, timeout=3)

    @classmethod
    def create_index(cls, index_name):
        """
        Creates custom index
        :param index_name: name of the index to be created
        """
        if cls.enterprise_cloud:
            data_dict = {
                "name": index_name,
                "maxGlobalRawDataSizeMB": "10240",
                "frozenTimePeriodInSecs": "31536000",
            }
            retries = 0
            while retries < 3:
                response = requests.post(
                    cls.splunk_url + cls.enterprise_cloud_index_endpoint,
                    auth=(cls.username, cls.password),
                    verify=False,
                    data=data_dict,
                )
                if response.status_code != 200 and response.status_code != 201:
                    cls.logger.error(
                        "error while creating index= {} at {}. Recieved {} response code".format(
                            index_name, cls.splunk_url, response.status_code
                        )
                    )
                    cls.logger.error(response.text)
                    retries += 1
                    time.sleep(1 * 10)
                else:
                    cls.logger.info("{} index successfully created.".format(index_name))
        else:
            payload = {"name": index_name}
            cls.rest.create_index(**payload)

    @classmethod
    def delete_index(cls, index_name):
        """
        Deletes custom index
        :param index_name: name of the index to be deleted
        """
        cls.rest.delete_index(index_name)

    @classmethod
    def enable_proxy_configuration(cls):
        """
        Enables the proxy configuration
        """
        secret_key_name = cls.get_secret_key_name("proxy", "password")
        secret_config = {"name": secret_key_name, "password": cls.PROXY_PASSWORD}
        cls.rest.create_secret(**secret_config)
        proxy_config = {
            "disabled": "false",
            "password": "********",
            "port": cls.PROXY_PORT,
            "host": cls.PROXY_HOST,
            "username": cls.PROXY_USERNAME,
        }
        cls.rest.edit_office_settings("proxy", **proxy_config)

    @classmethod
    def disable_proxy_configuration(cls):
        """
        Disables the proxy configuration
        """
        proxy_config = {
            "disabled": "true",
            "password": "********",
            "port": cls.PROXY_PORT,
            "host": cls.PROXY_HOST,
            "username": cls.PROXY_USERNAME,
        }
        cls.rest.edit_office_settings("proxy", **proxy_config)

    def remove_checkpoint_from_test_runner(self, input_file):
        try:
            os.remove(input_file)
            self.logger.info(
                "Checkpoint file removed successfully from test runner {0}".format(
                    input_file
                )
            )
        except Exception as e:
            self.logger.error(
                "Error while removing file from test runner - {0}".format(e)
            )

    @classmethod
    def remove_checkpoint(cls, remove_checkpoint_dict):
        def remove_ckp(input_type, input_file):

            ckp_file = cls._get_ckp_file(input_file, input_type)
            status, _ = cls.rest.delete_checkpoint_input("delete", file_path=ckp_file)

            if not status:
                # status,_,_ = cls.ssh_conn.execute("rm -rf {0}".format(ckp_file))
                if not status:
                    cls.logger.info(
                        "Checkpoint file removed successfully - {0}".format(ckp_file)
                    )
                else:
                    cls.logger.error(
                        "Checkpoint file exists but error in removing file - {0}".format(
                            ckp_file
                        )
                    )
            else:
                cls.logger.warning(
                    "Checkpoint file does not exist -  {0}".format(ckp_file)
                )

        for input_type, value in remove_checkpoint_dict.items():
            if isinstance(value, basestring):
                return remove_ckp(input_type, value)
            else:
                for file_name in value:
                    remove_ckp(input_type, file_name)

    @classmethod
    def get_checkpoint(cls, input_name, input_type):
        input_file = input_name + ".ckpt"
        ckp_file = cls._get_ckp_file(input_file, input_type)

        status, test = cls.rest.get_checkpoint_input(
            "read", file_path=ckp_file, base64="1", output_mode="json"
        )

        # if status:
        #     cls.logger.warning('Checkpoint file does not exist - {0}'.format(ckp_file))
        #     return None
        # status,stdout,_ = cls.ssh_conn.execute("cat {0}".format(ckp_file))
        if status:
            checkpoint_file = open(input_file, "wb")
            payload = json.loads(test)
            file_contents = base64.decodebytes(
                payload["entry"][0]["content"]["file_content"].encode("utf-8")
            )
            checkpoint_file.write(file_contents)
            checkpoint_file.close()
        content_list = cls.get_ckp_file_contents(input_file)
        return content_list

    @classmethod
    def _get_ckp_file(cls, input_name, input_type):
        ckp_file_name = input_name
        if input_type == "SERVICE_STATUS":
            ckp_file = os.path.join(
                cls.splunk_home, cls.CKP_FILEPATH_SERVICE_STATUS, ckp_file_name
            )
        elif input_type == "MANAGEMENT_ACTIVITY":
            ckp_file = os.path.join(
                cls.splunk_home, cls.CKP_FILEPATH_MANAGEMENT_ACTIVITY, ckp_file_name
            )
        else:
            ckp_file = os.path.join(
                cls.splunk_home, cls.CKP_FILEPATH_SERVICE_MESSAGE, ckp_file_name
            )
        return ckp_file

    @classmethod
    def get_ckp_file_contents(cls, file_name):
        try:
            fp = open(file_name, "rb")
            fp.seek(0, os.SEEK_END)
            end = fp.tell()
            fp.seek(0, os.SEEK_SET)
            content_dict = {}
            magic = fp.read(4)
            if magic != b"BUK0":
                cls.logger.error("magic mismatch")
                return None
            while True:
                position = fp.tell()
                if position >= end:
                    break
                try:
                    flag, key, expiration = umsgpack.unpack(fp)
                    if flag not in [1, 0]:
                        cls.logger.error("Data corrupted {0}".format(position))
                        return None
                except Exception as e:
                    cls.logger.error(
                        "Data corrupted {0}. Exception - {1} ".format(position, e)
                    )
                    return None
                else:
                    content_dict[key] = expiration
        except Exception as e:
            cls.logger.error("Exception: {0}".format(e))
            return None
        finally:
            fp.close()

        return content_dict

    @classmethod
    def get_secret_key_name(cls, stanzaname, key):
        if stanzaname and key:
            return "splunk_ta_o365_" + stanzaname + "_" + key
        return None

    @classmethod
    def delete_kv_store_checkpoint(cls, collection_name):

        kvstore_endpoint = "{}/servicesNS/{}/{}/storage/collections/data/{}".format(
            cls.splunk_url, cls.TA_APP_USER, cls.TA_APP_NAME, collection_name
        )
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer {}".format(cls.session_key),
        }
        response = requests.delete(kvstore_endpoint, headers=headers, verify=False)

    @classmethod
    def get_kv_store_checkpoint(cls, collection_name):

        kvstore_endpoint = "{}/servicesNS/{}/{}/storage/collections/data/{}".format(
            cls.splunk_url, cls.TA_APP_USER, cls.TA_APP_NAME, collection_name
        )
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer {}".format(cls.session_key),
        }
        response = requests.get(kvstore_endpoint, headers=headers, verify=False)
        return json.loads(response.text)
