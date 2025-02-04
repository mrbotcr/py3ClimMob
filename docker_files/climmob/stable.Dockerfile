FROM mrbotcr/climmob_base:20240828

MAINTAINER MrBot Software Solutions

WORKDIR /opt/new_r_code
RUN git pull origin master
RUN Rscript /root/R_packages_installation/check_R_libraries.R

WORKDIR /opt
RUN mkdir climmob_repository && mkdir climmob_log && mkdir climmob_celery && mkdir climmob_plugins && mkdir climmob_gunicorn && mkdir climmob_config
VOLUME /opt/climmob_repository

VOLUME /opt/climmob_log

VOLUME /opt/climmob_celery

VOLUME /opt/climmob_plugins

VOLUME /opt/climmob_config

RUN python3 -m venv climmob_env && git clone https://github.com/mrbotcr/py3ClimMob.git -b develop climmob && . ./climmob_env/bin/activate && pip install wheel && pip install -r /opt/climmob/requirements.txt && python /opt/climmob/download_nltk_packages.py

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.6.0/wait /wait
RUN chmod +x /wait

COPY docker_files/etc/default/celery_climmob /etc/default/celery_climmob
COPY docker_files/etc/init.d/celery_climmob /etc/init.d/celery_climmob
COPY ./docker_files/run_server.sh /opt/climmob_gunicorn
COPY ./docker_files/docker-entrypoint.sh /

EXPOSE 5900

RUN chmod +x /docker-entrypoint.sh && chmod +x /etc/init.d/celery_climmob && chmod +x /opt/climmob_gunicorn/run_server.sh && chmod 640 /etc/default/celery_climmob

RUN ldconfig
ENTRYPOINT ["/docker-entrypoint.sh"]