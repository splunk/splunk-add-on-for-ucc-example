import os
import sys
import time
import pytest
from random import randint

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "centaurs"))
from tacommon.test_ta_check_helper import TestTACheckHelper
from .O365TATest import O365TATest


class TestO365ManagementActivityInput(O365TATest):
    def config_utility(
        self,
        task_name,
        content_type,
        workload,
        index_name=None,
        source=None,
        delete=True,
        wait=True,
    ):
        """
        Utility method for creating and deleting inputs
        :param task_name: name of the input
        :param content_type: type of content for the input
        :param workload: workload to search for
        :param index_name: name of the index to ingest data
        :param source: source to search for
        :return boolean value based on the result of search
        """
        if not index_name:
            index_name = task_name + "_" + str(randint(0, 10000000))
        configs = self.get_config(task_name, index_name, content_type)
        self.create_index(configs["index"])
        self.create_management_activity_task(configs)
        # time.sleep(self.SLEEP_TIME)

        search_string = (
            'index={} source!=*eventgen* sourcetype="o365:management:activity" '.format(
                index_name
            )
        )
        search_string += "source=" + source if source else "Workload=" + workload

        result = True
        if wait:
            result = TestTACheckHelper.fetch_and_exit(
                self.splunk,
                search_string,
                secondsToStable=self.SLEEP_TIME,
                retry_interval=self.RETRY_INTERVAL,
            )
        if delete:
            self.delete_management_activity_task(task_name)

        return result

    def remove_checkpoint_task(self, task_name):
        """
        Utility to remove checkpoint from splunk in teardown method
        """
        remove_ckpt_dict = {"task_name": task_name, "task_type": "MANAGEMENT_ACTIVITY"}
        self.remove_checkpoints.append(remove_ckpt_dict)

    @pytest.mark.execute_enterprise_cloud_true
    def test_audit_ad_input(self, audit_ad_gen):
        """
        Test the data collection with 'Audit.AzureActiveDirectory' content type of management activity input
        """
        task_name = "task_azure_ad_input"
        self.disable_proxy_configuration()
        self.remove_checkpoint_task(task_name)
        assert self.config_utility(
            task_name=task_name,
            content_type="Audit.AzureActiveDirectory",
            workload="AzureActiveDirectory",
        )

    @pytest.mark.execute_enterprise_cloud_false
    def task_azure_ad_input_with_proxy(self, audit_ad_gen):
        """
        Test the data collection with 'Audit.General' content type of management activity input with proxy
        """
        task_name = "task_azure_general_input_with_proxy"
        self.remove_checkpoint_task(task_name)
        self.enable_proxy_configuration()
        task_name = "task_azure_ad_input"
        self.remove_checkpoint_task(task_name)
        result = self.config_utility(
            task_name=task_name,
            content_type="Audit.AzureActiveDirectory",
            workload="AzureActiveDirectory",
        )
        self.disable_proxy_configuration()
        assert result

    @pytest.mark.execute_enterprise_cloud_true
    def test_audit_exchange_input(self, audit_exchange_gen):
        """
        Test the data collection with 'Audit.Exchange' content type of management activity input
        """
        task_name = "task_azure_exchange_input"
        self.remove_checkpoint_task(task_name)
        assert self.config_utility(
            task_name=task_name, content_type="Audit.Exchange", workload="Exchange"
        )

    @pytest.mark.execute_enterprise_cloud_true
    def test_audit_sharepoint_input(self, audit_sharepoint_gen):
        """
        Test the data collection with 'Audit.SharePoint' content type of management activity input
        """
        task_name = "task_azure_sharepoint_input"
        self.remove_checkpoint_task(task_name)
        assert self.config_utility(
            task_name=task_name, content_type="Audit.SharePoint", workload="SharePoint"
        )

    @pytest.mark.execute_enterprise_cloud_true
    def test_audit_general_input(self, audit_ad_gen):
        """
        Test the data collection with 'Audit.General' content type of management activity input
        """
        task_name = "task_azure_general_input"
        self.remove_checkpoint_task(task_name)
        assert self.config_utility(
            task_name=task_name, content_type="Audit.General", workload="*"
        )

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.skip
    def test_dlp_all_input(self):
        """
        Test the data collection with 'DLP.All' content type of management activity input
        """
        task_name = "task_dlp_all_input"
        self.remove_checkpoint_task(task_name)
        assert self.config_utility(
            task_name=task_name, content_type="DLP.All", workload="", source="*dlp_all*"
        )

    # @pytest.mark.execute_enterprise_cloud_false
    # def test_audit_general_input_with_proxy(self):
    #     """
    #     Test the data collection with 'Audit.General' content type of management activity input with proxy
    #     """
    #     task_name = "task_azure_general_input_with_proxy"
    #     self.remove_checkpoint_task(task_name)
    #     index_name = "audit_general_with_proxy"
    #     self.create_index(index_name)
    #     self.enable_proxy_configuration()
    #     result = self.config_utility(
    #         task_name=task_name, content_type="Audit.General", workload="SecurityComplianceCenter", index_name=index_name)  #https://compliance.microsoft.com/
    #     self.disable_proxy_configuration()
    #     assert result

    @pytest.mark.execute_enterprise_cloud_true
    def test_multiple_audit_ad_input(self, audit_ad_gen):
        """
        Test the multiple input data collection with 'Audit.General' content type of management activity input
        """
        base_index_name = "audit_ad_" + str(randint(0, 10000000))
        base_task_name = "task_azure_ad_input_"
        for i in range(1):
            index_name = base_index_name + str(i)
            self.create_index(index_name)
            task_name = base_task_name + str(i)
            self.disable_proxy_configuration()
            self.remove_checkpoint_task(task_name)
            self.config_utility(
                task_name=task_name,
                index_name=index_name,
                content_type="Audit.AzureActiveDirectory",
                workload="AzureActiveDirectory",
                wait=False,
                delete=False,
            )

        time.sleep(self.SLEEP_TIME)

        for i in range(1):
            index_name = base_index_name + str(i)
            task_name = base_task_name + str(i)
            self.remove_checkpoint_task(task_name)
            search_string = 'index="{}"'.format(index_name)
            result = TestTACheckHelper.fetch_and_exit(
                self.splunk,
                search_string,
                secondsToStable=self.SLEEP_TIME,
                retry_interval=self.RETRY_INTERVAL,
            )
            self.delete_management_activity_task(task_name)
            assert result

    def checkpoint_test(self, task_name, content_type, workload, source=None):
        """
        Test to check check checkpoint value is stored correctly or not
        :param task_name: name of the input
        :param content_type: type of content for the input
        :param workload: workload to search for
        """
        collection_name = "splunk_ta_o365_management_activity_{}".format(task_name)
        # clear checkpoint data
        self.delete_kv_store_checkpoint(collection_name)

        assert self.config_utility(
            task_name=task_name,
            content_type=content_type,
            workload=workload,
            source=source,
            delete=False,
        )

        checkpoint_old = self.get_kv_store_checkpoint(collection_name)
        assert checkpoint_old is not None

        self.delete_task = {"task_name": task_name, "task_type": "MANAGEMENT_ACTIVITY"}

        current_time = time.time()
        time.sleep(self.SLEEP_TIME)

        checkpoint_new = self.get_kv_store_checkpoint(collection_name)
        assert checkpoint_new is not None

        copy_checkpoint_new = checkpoint_new.copy()
        for new_cktp in copy_checkpoint_new:
            if new_cktp in checkpoint_old:
                checkpoint_old.remove(new_cktp)
            else:
                assert new_cktp["expiration"] > current_time
            checkpoint_new.remove(new_cktp)
        assert len(checkpoint_new) == 0

        copy_checkpoint_old = checkpoint_old.copy()
        for old_ckpt in copy_checkpoint_old:
            assert old_ckpt["expiration"] > current_time
            checkpoint_old.remove(old_ckpt)
        assert len(checkpoint_old) == 0

    @pytest.mark.execute_enterprise_cloud_true
    def test_audit_ad_checkpoint(self):
        """
        Test the checkpoint created for 'Audit.AzureActiveDirectory' content type
        """

        task_name = "test_audit_ad_checkpoint"
        content_type = "Audit.AzureActiveDirectory"
        workload = "AzureActiveDirectory"
        self.checkpoint_test(task_name, content_type, workload)

    @pytest.mark.execute_enterprise_cloud_true
    def test_audit_exchange_checkpoint(self):
        """
        Test the checkpoint created for 'Audit.Exchange' content type
        """

        task_name = "test_audit_exchange_checkpoint"
        content_type = "Audit.Exchange"
        workload = "Exchange"
        self.checkpoint_test(task_name, content_type, workload)

    @pytest.mark.execute_enterprise_cloud_true
    def test_audit_sharepoint_checkpoint(self):

        """
        Test the checkpoint created for 'Audit.SharePoint' content type
        """

        task_name = "test_audit_sharepoint_checkpoint"
        content_type = "Audit.SharePoint"
        workload = "SharePoint"
        self.checkpoint_test(task_name, content_type, workload)

    @pytest.mark.execute_enterprise_cloud_true
    def test_audit_general_checkpoint(self):
        """
        Test the checkpoint created for 'Audit.General' content type
        """

        task_name = "test_audit_general_checkpoint"
        content_type = "Audit.General"
        workload = "*"
        self.checkpoint_test(task_name, content_type, workload)

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.skip
    def test_dlp_all_checkpoint(self):
        """
        Test the checkpoint created for 'DLP.All' content type
        """

        task_name = "task_dlp_all_input"
        content_type = "DLP.All"
        workload = ""
        source = "*dlp_all*"
        self.checkpoint_test(task_name, content_type, workload, source)
