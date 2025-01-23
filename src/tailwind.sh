#!/bin/bash

read -p 'output filepath: ' out
npx @tailwindcss/cli -i ./static/terminusgps/css/input.css -o $out --minify
