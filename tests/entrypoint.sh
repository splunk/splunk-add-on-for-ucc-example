#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##

cd /home/circleci/work
ls -la 
pytest --splunk-host=splunk --splunkweb-port=8000 --splunk-port=8089 --splunk-password=Chang3d!
pytest --splunk-host=$1 --splunkweb-port=$2 --splunk-port=$3 --splunk-password=Chang3d!  
touch /home/circleci/work/docker_exit
