#!/bin/bash


if [ "$TRAVIS_OS_NAME" == "linux" ]; then
	sudo apt-get update -qq
	sudo apt-get install -y debhelper libc-ares-dev libssl-dev libwrap0-dev python-all python3-all uthash-dev xsltproc docbook-xsl libcunit1-dev libcjson-dev
fi

if [ "$TRAVIS_OS_NAME" == "osx" ]; then
	brew update
	brew install c-ares cjson openssl libwebsockets
fi

sudo pip install paho-mqtt
