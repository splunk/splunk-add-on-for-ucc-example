#!/bin/sh
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-1-2020
##
##
echo "Starting SauceLabs Connection..."
curl https://saucelabs.com/downloads/sc-4.4.12-linux.tar.gz -o /home/circleci/saucelabs.tar.gz
tar -xzf /home/circleci/saucelabs.tar.gz --directory /home/circleci/
/home/circleci/sc-4.4.12-linux/bin/sc -u ta-factory-01 -k be7beeab-8bba-420c-90b3-8eac2d16d3ca -i myTunnelO1 --no-remove-colliding-tunnels -v &
wget --retry-connrefused --no-check-certificate -T 10 localhost:4445

cd /home/circleci/work
ls -la 
pytest --splunk-host=splunk --splunkweb-port=8000 --splunk-port=8089 --splunk-password=Chang3d!
pytest --splunk-host=$1 --splunkweb-port=$2 --splunk-port=$3 --splunk-password=Chang3d!  
touch /home/circleci/work/docker_exit
