# Use Ubuntu as the base image
FROM ubuntu:latest

RUN apt-get -y update && apt-get -y install curl && apt-get install -y python3
ENV PYTHON3=/usr/lib/python3

RUN curl https://raw.githubusercontent.com/ajenti/ajenti/master/scripts/install.sh | bash -s -

RUN apt-get install -y nodejs npm
RUN npm -g install bower babel-cli babel-preset-es2015 babel-plugin-external-helpers less coffee-script angular-gettext-cli angular-gettext-tools

RUN pip3 install ajenti-dev-multitool

RUN mkdir /opt/plugins
RUN touch /etc/ajenti/smtp.yml

# Expose the default Ajenti port
EXPOSE 8000

WORKDIR /opt/plugins/ajenti-threema

# Start Ajenti service
CMD ajenti-dev-multitool --run-dev 
