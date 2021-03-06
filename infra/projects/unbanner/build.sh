#!/bin/bash

echo "Building Unbanner..."

cd ../../../unbanner

rm -f unbanner.zip
rm -rf temp

mkdir -p temp/lib
rm -rf target && mkdir target

cp -a app/src/. temp/src
find temp/ | grep -E "(__pycache__|\.DS_Store|\.pyc|\.pyo$)" | xargs rm -rf

docker run --rm -u $(id -u):$(id -g) -v $PWD/:/usr/src/app python:3.6 pip install --no-cache-dir -r /usr/src/app/requirements/requirements.txt -t /usr/src/app/temp
 
cd temp && zip -r9 ../target/unbanner.zip * && cd ..
rm -rf temp
