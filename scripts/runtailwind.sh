#!/bin/bash

case "${1}" in
    "") npx tailwindcss -i ./global_static/css/input.css -o ./global_static/css/main.css --watch;;
    mini) npx tailwindcss -i ./global_static/css/input.css -o ./global_static/css/main.css --minify;;
    *) echo "Unknown option '${1}'"; exit 1;;
esac
