#!/bin/sh
set -e
: "${BACKEND_HOST:=backend}"
: "${BACKEND_PORT:=8000}"
export BACKEND_HOST BACKEND_PORT
envsubst '$BACKEND_HOST $BACKEND_PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;'
