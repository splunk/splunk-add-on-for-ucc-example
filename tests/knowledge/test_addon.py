#
# SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
# SPDX-License-Identifier: LicenseRef-Splunk-1-2020
#
#
import pytest
import requests
from pytest_splunk_addon.standard_lib.addon_basic import Basic


class Test_App(Basic):
    def empty_method(self):
        if 1 == 1:
            pass

    def dummy_method(self):
        url="https://splunk.com/this/is/dummy/url/to/test"
        res = requests.get(url)
        print(res)

