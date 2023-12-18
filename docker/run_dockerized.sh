#!/bin/sh

docker run -it -p 8000:8000 -v $PWD:/opt/plugins/ajenti-threema -e THREEMA_CONFIG=/opt/plugins/ajenti-threema/threema.yml ajenti_plugin_dev