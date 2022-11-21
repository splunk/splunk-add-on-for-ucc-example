import os
import sys
import time
import pytest
from random import randint

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "centaurs"))
from tacommon.test_ta_check_helper import TestTACheckHelper
from .O365TATest import O365TATest


class TestO365GraphApiInput(O365TATest):
    def config_utility(
        self,
        task_name,
        content_type,
        source_type=None,
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
        self.create_splunk_ta_o365_graph_api_task(configs)
        # time.sleep(self.SLEEP_TIME)

        search_string = 'index={} source="{}" '.format(index_name, source)

        result = True
        if wait:
            result = TestTACheckHelper.fetch_and_exit(
                self.splunk, search_string, secondsToStable=self.SLEEP_TIME
            )
        if delete:
            self.delete_splunk_ta_o365_graph_api_task(task_name)

        return result

    def remove_checkpoint_task(self, task_name):
        """
        Utility to remove checkpoint from splunk in teardown method
        """
        remove_ckpt_dict = {"task_name": task_name, "task_type": "MANAGEMENT_ACTIVITY"}
        self.remove_checkpoints.append(remove_ckpt_dict)

    @pytest.mark.execute_enterprise_cloud_true
    @pytest.mark.skip(
        reason="Data generation can not be automated for serviceAnnouncement since they are vendor dependent"
    )
    @pytest.mark.parametrize(
        "content_type,source",
        [
            ("serviceAnnouncement.messages", "serviceAnnouncement.messages"),
            ("serviceAnnouncement.issues", "serviceAnnouncement.issues"),
        ],
    )
    def test_graph_api_input(self, content_type, source):
        """
        Test the data collection with 'serviceAnnouncement.messages' content type of management activity input
        """
        task_name = "task_azure_graph_{}_{}".format(
            content_type.replace(".", "_"), str(randint(0, 10000))
        )
        self.disable_proxy_configuration()
        self.remove_checkpoint_task(task_name)
        assert self.config_utility(
            task_name=task_name, content_type=content_type, source=source
        )
