#!/bin/sh

if [ -z "$1" ]; then
  echo "Error: No argument provided. Specify a relative path to the script, starting from the project's root dir."
  exit 1
fi

docker run --rm -it -p 8000:8000 -v $PWD:/opt/plugins/ajenti-threema -e THREEMA_CONFIG=/opt/plugins/ajenti-threema/threema.yml ajenti_plugin_dev /usr/bin/python3 /opt/plugins/ajenti-threema/$1