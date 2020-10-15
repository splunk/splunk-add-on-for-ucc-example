#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

cd /home/circleci/work
if [ ${TEST_SET} -eq "tests/ui" ]; then
    echo "Hello1"
    cp /home/circleci/work/tests/pytest-ko.ini /home/circleci/work/tests/pytest.ini
    echo "Hello"
else
    cp /home/circleci/work/tests/pytest-ci.ini /home/circleci/work/tests/pytest.ini
fi
echo Test Args $@ ${TEST_SET}
pytest $@ ${TEST_SET}
