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

echo "Check Saucelab connection..."
wget --retry-connrefused --no-check-certificate -T 10 sauceconnect:4445

echo "Executing Tests..."

if [ -z ${TEST_BROWSER} ] 
then
    echo Test Args $@ ${TEST_SET}
    pytest $@ ${TEST_SET}
    test_exit_code=$?
else
    echo Test Args $@ --browser=${TEST_BROWSER} ${TEST_SET}
    pytest $@ --browser=${TEST_BROWSER} ${TEST_SET}
    test_exit_code=$?
fi
exit "$test_exit_code"