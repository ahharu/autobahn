#!/bin/bash -e

if [[ -z "$1" ]]; then
    echo "Stage not provided"
      exit 1
    fi

    cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" &&
      ./build.sh
    cd infra/common &&
      npm install &&
      serverless deploy --stage $1 --profile default
