#!/bin/bash
service postgresql start
sleep 30
python3 -m Stock_DB
