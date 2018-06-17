#!/bin/bash

cd ../../../elb_bot_detector

virtualenv_name=elb_bot_detector

workon=$HOME/.$virtualenv_name

if [[ ! -d "$workon" ]]; then
   virtualenv -p /usr/bin/python3 $workon
fi

source $workon/bin/activate

cd app
rm -rf ../home
mkdir -p ../home

INSTALL_DEPENDENCIES='pip install --user --no-cache-dir unittest-xml-reporting -r /usr/src/app/requirements/test.txt'
CD_APP_DIR='cd /usr/src/app/app'
GENERATE_TEST_REPORTS='python -m xmlrunner discover -p "*Test.py" && python -m xmlrunner discover -p "*IT.py"'

docker run --rm -u $(id -u):$(id -g) -e HOME=/usr/src/app/home -v $PWD/..:/usr/src/app -v $HOME/$virtualenv_name/.cache:/usr/src/app/home/.cache python:3.6 /bin/bash -c "$INSTALL_DEPENDENCIES  && $CD_APP_DIR && export PATH=$PATH:/usr/src/app/home/.local/bin && $GENERATE_TEST_REPORTS"

rm -rf ../home