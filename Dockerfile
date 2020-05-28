FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

# prepare system
RUN apt-get update && apt-get install wget git build-essential python3-dev python3-pip software-properties-common \
    postgresql-server-dev-10 postgresql-plpython3-10 ca-certificates -y

# setup postgres
COPY postgres.conf /etc/postgresql/10/main/conf.d/cgrdb.conf
RUN echo "PATH = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'" >> /etc/postgresql/10/main/environment
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE SCHEMA reactions;" && \
    psql --command "ALTER USER postgres WITH PASSWORD 'afirdb';"
USER root

# install CGRdb
RUN git clone https://github.com/stsouko/smlar.git && \
    cd smlar && USE_PGXS=1 make && USE_PGXS=1 make install && cd .. & rm -rf smlar && \
    pip3 install compress-pickle git+https://github.com/cimm-kzn/CGRtools.git@master#egg=CGRtools[MRV] \
    git+https://github.com/stsouko/CIMtools.git@master#egg=CIMtools \
    git+https://github.com/pandylandy/CGRdbData.git@master#egg=CGRdbData \
    git+https://github.com/stsouko/CGRdb.git@master#egg=CGRdb[postgres] \
    LazyPony==0.3.2

# setup CGRdb
COPY config.json config.json
RUN service postgresql start && cgrdb init -p afirdb && cgrdb create -p afirdb --name reactions --config config.json && rm config.json && service postgresql stop
RUN echo "listen_addresses='*'" >> /etc/postgresql/10/main/postgresql.conf
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/10/main/pg_hba.conf
#VOLUME ["/var/log/postgresql", "/var/lib/postgresql"]
EXPOSE 5432
USER postgres
CMD ["/usr/lib/postgresql/10/bin/postgres", "-D", "/var/lib/postgresql/10/main", "-c", "config_file=/etc/postgresql/10/main/postgresql.conf"]
#ENTRYPOINT ["/opt/boot"]