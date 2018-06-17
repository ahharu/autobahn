#!/bin/bash

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
for project in infra/projects/*; do
  echo $PWD
  cd $project
  if [ -f "generate_reports.sh" ]; then
    ./generate_reports.sh
  fi
  cd $BASEDIR
done