#!/bin/bash

if [ ! -f "docker-compose.yml" ]; then
    echo "Error: This script must be run from the bancho.py root directory"
    exit 1
fi

cd guweb

if [ -d "temp_guweb" ]; then
    rm -rf temp_guweb
fi

git clone https://github.com/varkaria/guweb.git temp_guweb

if [ $? -ne 0 ]; then
    echo "Error: Failed to clone guweb repository"
    exit 1
fi


if [ -f "config.py" ]; then
    cp config.py config.py.backup
fi

cp -rn temp_guweb/blueprints/* blueprints/ 2>/dev/null || true
cp -rn temp_guweb/constants/* constants/ 2>/dev/null || true
cp -rn temp_guweb/objects/* objects/ 2>/dev/null || true
cp -r temp_guweb/templates . 2>/dev/null || true
cp -r temp_guweb/static . 2>/dev/null || true
cp -r temp_guweb/docs . 2>/dev/null || true

if [ ! -f "LICENSE" ]; then
    cp temp_guweb/LICENSE . 2>/dev/null || true
fi

rm -rf temp_guweb

mkdir -p .data/avatars
mkdir -p .data/banners
mkdir -p .data/backgrounds
