#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

curl https://saucelabs.com/downloads/sc-4.4.12-linux.tar.gz -o /home/circleci/work/saucelabs.tar.gz
tar -xzf /home/circleci/work/saucelabs.tar.gz --directory /home/circleci/work/
cd /home/circleci/work/sc-*
/home/circleci/work/sc-4.4.12-linux/bin/sc -u ta-factory-01 -k be7beeab-8bba-420c-90b3-8eac2d16d3ca &
wget --retry-connrefused --no-check-certificate -T 10 localhost:4445

ls -la /home/circleci/work/
ip=$(head -n 1 /home/circleci/work/ip.txt)

echo "ip arg: $ip"
cd /home/circleci/work
ls -la 
pytest $@ --splunk-host=$ip
