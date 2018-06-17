#!/bin/bash -e

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
for project in infra/projects/*; do
  cd $project
  if [ -f "build.sh" ]; then
    ./build.sh
  fi
  cd $BASEDIR
done