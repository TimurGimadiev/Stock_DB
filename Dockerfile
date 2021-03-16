FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

# prepare system
RUN apt-get update && apt-get install wget git python3.8-dev python3-pip \
    postgresql-server-dev-12 postgresql-plpython3-12 nodejs -y

# setup postgres
COPY postgres.conf /etc/postgresql/12/main/conf.d/cgrdb.conf
USER postgres
RUN /etc/init.d/postgresql start && \
    #psql --command "CREATE SCHEMA molecules;" && \
    psql --command "ALTER USER postgres WITH PASSWORD 'stock_db';"
USER root

# install CGRdb
RUN pip3 install git+https://github.com/stsouko/CGRtools.git@master#egg=CGRtools[MRV,clean2d] \
    compress-pickle StructureFingerprint\
    git+https://github.com/stsouko/CGRdb.git@master#egg=CGRdb \
    git+https://github.com/pandylandy/CGRdbData.git@master#egg=CGRdbData \
    Dash dash_marvinjs numba xlrd XlsxWriter psycopg2cffi

# setup CGRdb
COPY config.json config.json
COPY TimeStamp /tmp/TimeStamp
RUN cd /tmp/TimeStamp && pip3 install . && rm -fr /tmp/TimeStamp && cd
RUN service postgresql start && sleep 30 &&\
 cgrdb init  -c '{"user":"postgres","password":"stock_db","host":"localhost"}' &&\
 cgrdb create -f config.json -c '{"user":"postgres","password":"stock_db","host":"localhost"}' -n "molecules" &&\
 rm config.json
#RUN echo "listen_addresses='*'" >> /etc/postgresql/12/main/postgresql.conf
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/12/main/pg_hba.conf
#VOLUME ["/var/lib/postgresql/12/main"]
#"/var/log/postgresql",
COPY Stock_DB /tmp/Stock_DB
COPY setup.py /tmp/
COPY README.md /tmp/
COPY boot.sh boot.sh
RUN cd /tmp && pip3 install . && rm -rf Stock_DB setup.py README.md && cd ..
COPY mjs /usr/local/lib/python3.8/dist-packages/Stock_DB/assets/mjs
COPY Stock_DB/assets/test.svg /usr/local/lib/python3.8/dist-packages/Stock_DB/assets/
#RUN cd Stock_DB
EXPOSE 8008 5432 8000
#RUN ls
USER postgres
CMD ["bash","boot.sh"]
#EXPOSE 5432
#USER postgres
#CMD ["/usr/lib/postgresql/12/bin/postgres", "-D", "/var/lib/postgresql/12/main", "-c", "config_file=/etc/postgresql/12/main/postgresql.conf"]
#ENTRYPOINT ["/opt/boot"]