#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

cd /home/circleci/work
if [ -f "${TEST_SET}/pytest-ci.ini" ]; then
    cp -f ${TEST_SET}/pytest-ci.ini ${TEST_SET}/pytest.ini
fi

# Installing the requirements 
pip install -r ${TEST_SET}/requirements.txt

cp -f .pytest.expect ${TEST_SET}
echo "Check Saucelab connection..."
wget --retry-connrefused --no-check-certificate -T 10 sauceconnect:4445

echo "Executing Tests..."
RERUN_COUNT=${RERUN_COUNT:-1}
if [ -z ${TEST_BROWSER} ] 
then
    # If the browser param is not provided 
    # then execute the knowledge, etc. tests
    echo Test Args $@ ${TEST_SET}
    pytest $@ ${TEST_SET}
    test_exit_code=$?
else
    # Execute the tests on Headless mode in local if UI_TEST_HEADLESS environment is set to "true"
    if [ "${UI_TEST_HEADLESS}" = "true" ]
    then
        echo Test Args $@ --local --persist-browser --headless --reruns=${RERUN_COUNT}  --browser=${TEST_BROWSER} ${TEST_SET}
        pytest $@ --local --persist-browser --headless --reruns=${RERUN_COUNT} --browser=${TEST_BROWSER} ${TEST_SET}
        test_exit_code=$?
    else
        # Execute the UI test cases on Saucelabs 
        echo Test Args $@ --reruns=${RERUN_COUNT} --browser=${TEST_BROWSER} ${TEST_SET}
        pytest $@ --reruns=${RERUN_COUNT} --browser=${TEST_BROWSER} ${TEST_SET}
        test_exit_code=$?
    fi
fi
exit "$test_exit_code"