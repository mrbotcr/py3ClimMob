FROM ubuntu:22.04

MAINTAINER MrBot Software Solutions
ENV CR=America/Costa_Rica
ENV DEBIAN_FRONTEND noninteractive
RUN ln -snf /usr/share/zoneinfo/$CR /etc/localtime && echo $CR > /etc/timezone
RUN apt-get update && apt-get -y upgrade && apt-get install -y software-properties-common && add-apt-repository universe && add-apt-repository multiverse

RUN apt-get install -y wget tzdata

# R
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN add-apt-repository -y 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'

RUN wget http://archive.ubuntu.com/ubuntu/pool/main/i/icu/libicu66_66.1-2ubuntu2_amd64.deb && dpkg -i ./libicu66_66.1-2ubuntu2_amd64.deb

# Mongo
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc |  gpg --dearmor | tee /usr/share/keyrings/mongodb.gpg > /dev/null
RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list

RUN apt-get update

RUN apt-get install -y build-essential qtbase5-dev qtbase5-private-dev qtdeclarative5-dev libqt5sql5-mysql libqt5webkit5-dev libqt5svg5-dev libqt5xmlpatterns5-dev cmake mongodb-org nano jq libboost-all-dev unzip zlib1g-dev automake npm redis-server libmysqlclient-dev git python3-venv texlive-extra-utils r-base libcurl4-openssl-dev pandoc pandoc-citeproc libfontconfig1-dev libcairo2-dev libudunits2-dev libgdal-dev xvfb sqlite3 libqt5sql5-sqlite libgmp3-dev libmpfr-dev tidy golang-go mysql-client-8.0 openjdk-17-jre-headless

# Firefox
RUN apt-get install -y libdbus-glib-1-2 libgtk2.0-0

RUN wget -O ~/Firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest&os=linux64"
RUN tar xjf ~/Firefox.tar.bz2 -C /opt/

RUN ln -s /opt/firefox/firefox /usr/bin/

#RUN echo "export MOZ_HEADLESS=1" >> /etc/bash.bashrc

# MySQL Shell
RUN wget https://dev.mysql.com/get/mysql-apt-config_0.8.29-1_all.deb
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC dpkg -i ./mysql-apt-config_0.8.29-1_all.deb

RUN apt-get update

RUN apt-get install -y mysql-shell

# Svg2png
RUN npm install svg2png -g --unsafe-perm

# Json2csv
RUN npm install -g json2csv

#WebKit's
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz
RUN tar xvfz geckodriver-v0.31.0-linux64.tar.gz && cp geckodriver /bin

#ODKTOOLS
RUN wget https://github.com/BurntSushi/xsv/releases/download/0.13.0/xsv-0.13.0-x86_64-unknown-linux-musl.tar.gz
RUN tar xvfz xsv-0.13.0-x86_64-unknown-linux-musl.tar.gz && cp xsv /bin

RUN git clone https://github.com/qlands/csv2xlsx.git
WORKDIR csv2xlsx
RUN go build && cp csv2xlsx /bin

WORKDIR /opt
RUN mkdir odktools-deps
RUN git clone https://github.com/qlands/odktools.git -b stable-2.4

WORKDIR /opt/odktools-deps
RUN wget https://github.com/mongodb/mongo-c-driver/releases/download/1.21.1/mongo-c-driver-1.21.1.tar.gz
RUN wget https://github.com/mongodb/mongo-cxx-driver/releases/download/r3.6.7/mongo-cxx-driver-r3.6.7.tar.gz
RUN wget https://github.com/jmcnamara/libxlsxwriter/archive/refs/tags/RELEASE_1.1.4.tar.gz
RUN wget https://github.com/stachenov/quazip/archive/refs/tags/v1.3.tar.gz
RUN git clone https://github.com/rgamble/libcsv.git

RUN tar xvfz mongo-c-driver-1.21.1.tar.gz
WORKDIR /opt/odktools-deps/mongo-c-driver-1.21.1
RUN mkdir build_here
WORKDIR /opt/odktools-deps/mongo-c-driver-1.21.1/build_here
RUN cmake ..
RUN make
RUN make install
WORKDIR /opt/odktools-deps

RUN tar xvfz mongo-cxx-driver-r3.6.7.tar.gz
WORKDIR /opt/odktools-deps/mongo-cxx-driver-r3.6.7
RUN mkdir build_here
WORKDIR /opt/odktools-deps/mongo-cxx-driver-r3.6.7/build_here
RUN cmake -DCMAKE_C_FLAGS:STRING="-O2 -fPIC" -DCMAKE_CXX_FLAGS:STRING="-O2 -fPIC" -DBSONCXX_POLY_USE_BOOST=1 -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..
RUN make
RUN make install
WORKDIR /opt/odktools-deps

RUN tar xvfz v1.3.tar.gz
WORKDIR /opt/odktools-deps/quazip-1.3
RUN mkdir build
WORKDIR /opt/odktools-deps/quazip-1.3/build
RUN cmake -DCMAKE_C_FLAGS:STRING="-fPIC" -DCMAKE_CXX_FLAGS:STRING="-fPIC" ..
RUN make
RUN make install
WORKDIR /opt/odktools-deps

RUN ln -s /usr/bin/aclocal-1.16 /usr/bin/aclocal-1.14 && ln -s /usr/bin/automake-1.16 /usr/bin/automake-1.14

RUN tar xvfz RELEASE_1.1.4.tar.gz
WORKDIR /opt/odktools-deps/libxlsxwriter-RELEASE_1.1.4
RUN mkdir build
WORKDIR /opt/odktools-deps/libxlsxwriter-RELEASE_1.1.4/build
RUN cmake ..
RUN make
RUN make install
WORKDIR /opt/odktools-deps

WORKDIR /opt/odktools-deps/libcsv
RUN ./configure
RUN make
RUN make install

WORKDIR /opt/odktools

RUN qmake
RUN make

WORKDIR /opt
RUN git clone https://github.com/mrbotcr/wkhtmltopdf.git
WORKDIR wkhtmltopdf
RUN qmake
RUN make -j 4
RUN make install

WORKDIR /opt
RUN git clone https://github.com/AgrDataSci/ClimMob-analysis.git new_r_code

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y locales \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG=en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

WORKDIR /root
RUN mkdir R_packages_installation

COPY ./docker_files/verificationFile.txt /root

COPY ./docker_files/R_packages_installation /root/R_packages_installation

RUN ls --recursive /root/R_packages_installation

RUN Rscript /root/R_packages_installation/caret.R

RUN Rscript /root/R_packages_installation/climatrends.R && Rscript /root/R_packages_installation/ClimMobTools.R

RUN Rscript /root/R_packages_installation/ggparty.R  && Rscript /root/R_packages_installation/ggplot2.R && Rscript /root/R_packages_installation/gosset.R && Rscript /root/R_packages_installation/gridExtra.R

RUN Rscript /root/R_packages_installation/gtools.R && Rscript /root/R_packages_installation/igraph.R && Rscript /root/R_packages_installation/janitor.R && Rscript /root/R_packages_installation/jsonlite.R

RUN Rscript /root/R_packages_installation/knitr.R && Rscript /root/R_packages_installation/leaflet.R && Rscript /root/R_packages_installation/mapview.R && Rscript /root/R_packages_installation/multcompView.R

RUN Rscript /root/R_packages_installation/nasapower.R && Rscript /root/R_packages_installation/partykit.R && Rscript /root/R_packages_installation/patchwork.R && Rscript /root/R_packages_installation/PlackettLuce.R

RUN Rscript /root/R_packages_installation/plotrix.R && Rscript /root/R_packages_installation/pls.R && Rscript /root/R_packages_installation/png.R && Rscript /root/R_packages_installation/psychotools.R

RUN Rscript /root/R_packages_installation/qvcalc.R && Rscript /root/R_packages_installation/remotes.R && Rscript /root/R_packages_installation/rmarkdown.R

RUN Rscript /root/R_packages_installation/lubridate.R && Rscript /root/R_packages_installation/ggchicklet.R && Rscript /root/R_packages_installation/phantomjs.R

RUN Rscript /root/R_packages_installation/check_R_libraries.R

#RUN Rscript /opt/new_r_code/modules/00_check_packages.R



