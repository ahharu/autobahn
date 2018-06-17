#!/bin/bash -e

if [[ -z "$1" ]]; then
  echo "Stage not provided"
  exit 1
fi

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" &&
cd infra &&
cd common &&
serverless remove --stage $1

