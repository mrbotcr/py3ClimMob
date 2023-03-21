#!/bin/bash
# This assumes that ClimMob is under the official docker container. Adjust if necessary
# Add an symbolic link to script in /etc/cron.daily
find /opt/climmob/climmob/static/ephemeral -name '*.js' -mmin +1440 -delete > /dev/null