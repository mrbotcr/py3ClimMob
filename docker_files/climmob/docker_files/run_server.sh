#! /bin/bash

/wait
mysql -h $MYSQL_HOST_NAME -u $MYSQL_USER_NAME --ssl-mode=DISABLED --password=$MYSQL_USER_PASSWORD --execute='CREATE SCHEMA IF NOT EXISTS climmobv4'
source /opt/climmob_env/bin/activate
cd /opt/climmob
# If development.ini does not exists then create the basic database
if ! [ -f "/opt/climmob_config/development.ini" ]; then
  mysql -h $MYSQL_HOST_NAME -u $MYSQL_USER_NAME --password=$MYSQL_USER_PASSWORD climmobv4 < /opt/climmob/docker_files/climmob/docker_files/base_db.sql
fi

python create_config.py --daemon --capture_output --mysql_host $MYSQL_HOST_NAME --mysql_user_name $MYSQL_USER_NAME --mysql_user_password $MYSQL_USER_PASSWORD --repository_path /opt/climmob_repository --odktools_path /opt/odktools --climmob_host $climmob_HOST --climmob_port $climmob_PORT --forwarded_allow_ip $FORWARDED_ALLOW_IP --pid_file /opt/climmob_gunicorn/climmob.pid --error_log_file /opt/climmob_log/error_log /opt/climmob_config/development.ini

ln -s /opt/climmob_config/development.ini ./development.ini
python configure_celery.py ./development.ini
python setup.py develop
python setup.py compile_catalog
disable_ssl ./development.ini
configure_alembic ./development.ini .
configure_mysql ./development.ini .
alembic upgrade head

deactivate
/etc/init.d/celery_climmob stop
/etc/init.d/celery_climmob start
source /opt/climmob_env/bin/activate
rm /opt/climmob_gunicorn/climmob.pid
pserve /opt/climmob/development.ini
tail -f /dev/null
