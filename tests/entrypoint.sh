#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

echo "ip arg: $1"
echo "web port arg: $2"
echo "port arg: $3"
cd /home/circleci/work
ls -la 
pip install pytest-timeout
pytest --splunk-host=$1 --splunkweb-port=$2 --splunk-port=$3 --splunk-password=Chang3d!  --timeout=300
tail -n 100 $(find . -name pytest_splunk_addon.log)
touch /home/circleci/work/docker_exit
