import copy
import time
import random
import string
from datetime import datetime, timedelta
import threading

import logging

logger = logging.getLogger(__name__)


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


SECONDS_TO_STABLE = 120


class TestTACheckHelper:
    # Helper methods
    @staticmethod
    def get_search_result(
        splunk, search_string, timeout=60, job_prefix="search", **kwargs
    ):
        """
        :param splunk:
        :param search_string:
        :param timeout:
        :param job_prefix:
        :param kwargs: **{'adhoc_search_level': 'verbose'} to get the verbose results
        :return:
        """
        job = splunk.jobs().create(f"{job_prefix} {search_string}", **kwargs)
        job.wait(timeout)
        job_results = job.get_results()
        return job_results

    @staticmethod
    def get_event_count(splunk, search_string, timeout=60):
        search_string_for_count = f"{search_string} | stats count"
        res = TestTACheckHelper.get_search_result(
            splunk, search_string_for_count, timeout=timeout
        )
        event_count = int(res.as_dict["count"][0])
        return event_count

    @staticmethod
    def retry_task_list(
        task_list, secondsToStable=SECONDS_TO_STABLE, retry_interval=3, retry_after=0
    ):
        remained_task_list = copy.copy(task_list)

        def run_task():
            logger.info(
                f"start retry task, remained task number: {len(remained_task_list)}"
            )
            tmp_task_list = filter(lambda task: not task(), remained_task_list)
            del remained_task_list[:]
            remained_task_list.extend(tmp_task_list)
            logger.info(
                f"end retry task, remained task number: {len(remained_task_list)}"
            )
            return not remained_task_list

        res = TestTACheckHelper.retry_task(
            run_task,
            secondsToStable=secondsToStable,
            retry_interval=retry_interval,
            retry_after=retry_after,
        )

        return res, remained_task_list

    @staticmethod
    def retry_task(
        task, secondsToStable=SECONDS_TO_STABLE, retry_interval=3, retry_after=0
    ):
        def try_sleep():
            time.sleep(retry_interval)

        begin_time = datetime.now()
        timeout_flag = False
        while True:
            if task():
                break
            if timeout_flag:
                return False
            current_time = datetime.now()
            if (current_time - begin_time).total_seconds() > secondsToStable:
                timeout_flag = True
            try_sleep()
        for _ in range(retry_after):
            if not task():
                return False
            try_sleep()

        return True

    @staticmethod
    def fetch_and_exit(
        splunk, search_string, secondsToStable=SECONDS_TO_STABLE, retry_interval=3
    ):
        def task():
            return TestTACheckHelper.get_event_count(splunk, search_string) > 0

        return TestTACheckHelper.retry_task(
            task, secondsToStable=secondsToStable, retry_interval=retry_interval
        )

    @staticmethod
    def fetch_list_and_exit(
        splunk,
        search_string_list,
        secondsToStable=SECONDS_TO_STABLE,
        retry_interval=3,
        retry_after=0,
    ):
        """
        :param splunk:
        :param search_string_list:
        :param secondsToStable:
        :param retry_interval:
        :param retry_after:
        :return: res(True/False, remained_task_list)
        """
        if not isinstance(search_string_list, (list, tuple)):
            raise TypeError("search_string_list should be a list or tuple")

        def task(_search_string):
            def _task():
                return TestTACheckHelper.get_event_count(splunk, _search_string) > 0

            return _task

        task_list = []
        for search_string in search_string_list:
            sub_task = task(search_string)
            task_list.append(sub_task)

        return TestTACheckHelper.retry_task_list(
            task_list,
            secondsToStable=secondsToStable,
            retry_interval=retry_interval,
            retry_after=retry_after,
        )

    @staticmethod
    def fetch_number_and_exit(
        splunk,
        number,
        search_string,
        secondsToStable=SECONDS_TO_STABLE,
        retry_interval=3,
        retry_after=2,
    ):
        def task(aim_number):
            def real_task():
                return (
                    TestTACheckHelper.get_event_count(splunk, search_string)
                    == aim_number
                )

            return real_task

        return TestTACheckHelper.retry_task(
            task(number),
            secondsToStable=secondsToStable,
            retry_interval=retry_interval,
            retry_after=retry_after,
        )

    @staticmethod
    def gen_random_string(length):
        return "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(length)
        )

    @staticmethod
    def gen_random_number(length):
        return "".join(random.choice(string.digits) for _ in range(length))

    @staticmethod
    def retry_and_execute_thread(
        retry_task,
        execute_task,
        secondsToStable=SECONDS_TO_STABLE,
        retry_interval=3,
        retry_after=0,
    ):
        def thread_target():
            logger.info(
                f"start retry_and_execute_thread. retry_task: {retry_task}, execute_task: {execute_task}"
            )
            if not TestTACheckHelper.retry_task(
                task=retry_task,
                secondsToStable=secondsToStable,
                retry_interval=retry_interval,
                retry_after=retry_after,
            ):
                error_message = f"Failed the retry_task: {retry_task}"
                logger.error(error_message)
                raise RuntimeError(error_message)

            logger.info(f"start the retry_task: {execute_task}")
            execute_task()

        res_thread = threading.Thread(target=thread_target)
        return res_thread

    @staticmethod
    def get_splunk_time(splunk, offset_time_second, format_string, timeout=60):
        search_string = (
            "index=_internal | head 1 "
            "| eval tnow = (now()-{}) "
            '| eval tnow=strftime(tnow, "{}") '
            "| fields tnow".format(offset_time_second, format_string)
        )
        results = TestTACheckHelper.get_search_result(splunk, search_string, timeout)
        tnow = results[0]["tnow"]
        return tnow

    @staticmethod
    def fetch_and_exit_from_now(
        splunk,
        search_string,
        offset_time_second=0,
        secondsToStable=SECONDS_TO_STABLE,
        retry_interval=3,
    ):

        mark_time = TestTACheckHelper.get_splunk_time(
            splunk, offset_time_second, "%m/%d/%Y:%H:%M:%S"
        )
        search_string += f' earliest = "{mark_time}"'
        return TestTACheckHelper.fetch_and_exit(
            splunk,
            search_string,
            secondsToStable=secondsToStable,
            retry_interval=retry_interval,
        )

    @staticmethod
    def fetch_number_and_exit_from_now(
        splunk,
        number,
        search_string,
        offset_time_second=0,
        secondsToStable=SECONDS_TO_STABLE,
        retry_interval=3,
        retry_after=2,
    ):

        mark_time = TestTACheckHelper.get_splunk_time(
            splunk, offset_time_second, "%m/%d/%Y:%H:%M:%S"
        )
        search_string += f' earliest = "{mark_time}"'
        return TestTACheckHelper.fetch_number_and_exit(
            splunk,
            number,
            search_string,
            secondsToStable=secondsToStable,
            retry_interval=retry_interval,
            retry_after=retry_after,
        )

    @staticmethod
    def fetch_list_and_exit_from_now(
        splunk,
        search_string_list,
        offset_time_second=0,
        secondsToStable=SECONDS_TO_STABLE,
        retry_interval=3,
        retry_after=0,
    ):
        """
        :param splunk:
        :param search_string_list:
        :param secondsToStable:
        :param retry_interval:
        :param retry_after:
        :return: res(True/False, remained_task_list)
        """
        mark_time = TestTACheckHelper.get_splunk_time(
            splunk, offset_time_second, "%m/%d/%Y:%H:%M:%S"
        )
        _search_string_list = map(
            lambda x: x + f' earliest = "{mark_time}"', search_string_list
        )
        return TestTACheckHelper.fetch_list_and_exit(
            splunk,
            _search_string_list,
            secondsToStable=secondsToStable,
            retry_interval=retry_interval,
            retry_after=retry_after,
        )
