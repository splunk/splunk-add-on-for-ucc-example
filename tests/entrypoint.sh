#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

curl https://saucelabs.com/downloads/sc-4.4.12-linux.tar.gz -o /home/circleci/work/tests/saucelabs.tar.gz
tar -xzf /home/circleci/work/tests/saucelabs.tar.gz --directory /home/circleci/work/tests/
cd /home/circleci/work/tests/sc-*
/home/circleci/work/tests/sc-4.4.12-linux/bin/sc -u ta-factory-01 -k be7beeab-8bba-420c-90b3-8eac2d16d3ca --doctor &
wget --retry-connrefused --no-check-certificate -T 6 localhost:4445

cd /home/circleci/work
pytest $@
