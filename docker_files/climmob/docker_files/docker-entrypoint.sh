#!/bin/bash

/etc/init.d/mongodb start
rm /var/run/redis/redis-server.pid
/etc/init.d/redis-server start

set -e

# Apache gets grumpy about PID files pre-existing
rm -f /opt/climmob_gunicorn/climmob.pid
rm -f /opt/climmob_celery/run/worker1.pid
exec /opt/climmob_gunicorn/run_server.sh