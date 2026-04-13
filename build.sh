#!/bin/bash

mkdir -p build
zip -r "build/bot.zip" * -x "build/*" -x "build.sh"