#!/bin/bash -e

if [[ -z "$1" ]]; then
  echo "Stage not provided"
  exit 1
fi

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" &&

cd infra &&
cd common &&
docker run --rm -u $(id -u):$(id -g) -e'HOME=/tmp' -v $BASEDIR:/opt/app amaysim/serverless:1.26.0 sh -c "cd infra/common && npm install && serverless decrypt --stage $1 --password '$SERVERLESS_DECRYPT_KEY' && serverless remove --stage $1"