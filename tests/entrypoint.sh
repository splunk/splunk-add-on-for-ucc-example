#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

cd /home/circleci/work
if exists ${TEST_SET}/pytest-ci.ini cp -f ./pytest.ini
echo Test Args $@ ${TEST_SET}
pytest $@ ${TEST_SET}
