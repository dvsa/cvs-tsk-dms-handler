#!/usr/bin/env bash

# pipenv stores the virtual env in a different directory so we need to get the path to it
SITE_PACKAGES=$(pipenv --venv)/lib/python3.7/site-packages
echo "Library Location: $SITE_PACKAGES"
DIR=$(pwd)

# Make sure pipenv is good to go
echo "Do fresh install to make sure everything is there"
pipenv --rm
pipenv install --deploy

cd ${SITE_PACKAGES}
7z a -tzip -mx=9 ${DIR}/package.zip * -xr!boto3 -x!boto3* -xr!botocore -x!botocore*
7z a -tzip -mx=9 ${DIR}/package.zip boto3_type_annotations*
cd ${DIR}
7z d ${DIR}/package.zip pip pip* setuptools setuptools* wheel wheel* pkg_resources pkg_resources* easy_install easy_install* *.dist-info -r
7z a -tzip -mx=9 package.zip dms-handler.py
