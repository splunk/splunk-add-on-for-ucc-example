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
echo Test Args $@ ${TEST_SET}
pytest $@ ${TEST_SET}