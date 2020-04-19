FROM stock_db_wui_data:latest

ENV DEBIAN_FRONTEND noninteractive
USER root
RUN pip3 install Dash dash_marvinjs numba
RUN LANG=en_US.UTF-8
# setup Stock_db
COPY Stock_DB Stock_DB
COPY boot.sh boot.sh
EXPOSE 8008 5432 8000
CMD ["bash","boot.sh"]
