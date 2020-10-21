#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

echo "ip arg: $1"
echo "web port arg: $2"
cd /home/circleci/work
ls -la 
pytest --splunk-host=$1 --splunkweb-port=$2 --splunk-password=Chang3d!
touch /home/circleci/work/docker_exit