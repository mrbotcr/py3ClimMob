FROM ubuntu:20.04

MAINTAINER Alianza Bioversity-CIAT
ENV CR=America/Costa_Rica
ENV DEBIAN_FRONTEND noninteractive
RUN ln -snf /usr/share/zoneinfo/$CR /etc/localtime && echo $CR > /etc/timezone
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y software-properties-common
RUN add-apt-repository universe && add-apt-repository multiverse
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN add-apt-repository -y 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'
RUN apt-get update

RUN apt-get install -y build-essential qt5-default qtbase5-private-dev qtdeclarative5-dev libqt5sql5-mysql libqt5webkit5-dev libqt5svg5-dev libqt5xmlpatterns5-dev cmake mongodb nano jq libboost-all-dev unzip zlib1g-dev automake npm redis-server libmysqlclient-dev mysql-client-8.0 git python3-venv texlive-extra-utils r-base libcurl4-openssl-dev pandoc pandoc-citeproc libfontconfig1-dev libcairo2-dev libudunits2-dev libgdal-dev xvfb sqlite3 libqt5sql5-sqlite libgmp3-dev libmpfr-dev tidy golang-go firefox wget

COPY ./docker_files/sqldriver/libqsqlmysql.s_o /usr/lib/x86_64-linux-gnu/qt5/plugins/sqldrivers/libqsqlmysql.so

#JDK-18
RUN apt install -y libc6-x32 libc6-i386
RUN wget https://download.oracle.com/java/18/latest/jdk-18_linux-x64_bin.deb
RUN apt-get install -y libasound2
RUN DEBIAN_FRONTEND=noninteractive dpkg -i jdk-18_linux-x64_bin.deb
RUN update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk-18/bin/java 1

RUN npm install svg2png -g --unsafe-perm

RUN npm install -g json2csv

#WebKit's
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz
RUN tar xvfz geckodriver-v0.31.0-linux64.tar.gz
RUN cp geckodriver /bin

#ODKTOOLS
RUN wget https://dev.mysql.com/get/mysql-apt-config_0.8.22-1_all.deb
RUN dpkg -i ./mysql-apt-config_0.8.22-1_all.deb
RUN apt-get update
RUN apt-get install mysql-shell

RUN wget https://github.com/BurntSushi/xsv/releases/download/0.13.0/xsv-0.13.0-x86_64-unknown-linux-musl.tar.gz
RUN tar xvfz xsv-0.13.0-x86_64-unknown-linux-musl.tar.gz
RUN cp xsv /bin

RUN git clone https://github.com/qlands/csv2xlsx.git
WORKDIR csv2xlsx
RUN go build
RUN cp csv2xlsx /bin

WORKDIR /opt
RUN mkdir odktools-deps
RUN git clone https://github.com/qlands/odktools.git

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

RUN ln -s /usr/bin/aclocal-1.16 /usr/bin/aclocal-1.14
RUN ln -s /usr/bin/automake-1.16 /usr/bin/automake-1.14

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
RUN git clone https://github.com/BioversityCostaRica/wkhtmltopdf.git
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

WORKDIR /opt

COPY ./docker_files/verificationFile.txt /opt
RUN Rscript ./new_r_code/modules/00_check_packages.R
COPY ./docker_files/check_R_libraries.R /opt
RUN Rscript /opt/check_R_libraries.R