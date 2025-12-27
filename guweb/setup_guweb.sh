#!/bin/bash

# guweb 초기 설정 스크립트

echo "==================================="
echo "guweb Setup for bancho.py"
echo "==================================="
echo ""

# 현재 디렉토리 확인
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: This script must be run from the bancho.py root directory"
    exit 1
fi

echo "Step 1: Cloning guweb repository..."
cd guweb

# 임시 디렉토리에 guweb 클론
if [ -d "temp_guweb" ]; then
    rm -rf temp_guweb
fi

git clone https://github.com/varkaria/guweb.git temp_guweb

if [ $? -ne 0 ]; then
    echo "Error: Failed to clone guweb repository"
    exit 1
fi

echo "Step 2: Copying guweb files..."

# 이미 존재하는 파일들 백업
if [ -f "config.py" ]; then
    cp config.py config.py.backup
    echo "Backed up config.py to config.py.backup"
fi

# 필요한 디렉토리와 파일 복사 (기존 파일 유지)
cp -rn temp_guweb/blueprints/* blueprints/ 2>/dev/null || true
cp -rn temp_guweb/constants/* constants/ 2>/dev/null || true
cp -rn temp_guweb/objects/* objects/ 2>/dev/null || true
cp -r temp_guweb/templates . 2>/dev/null || true
cp -r temp_guweb/static . 2>/dev/null || true
cp -r temp_guweb/docs . 2>/dev/null || true

# LICENSE 파일 복사 (선택)
if [ ! -f "LICENSE" ]; then
    cp temp_guweb/LICENSE . 2>/dev/null || true
fi

echo "Step 3: Cleaning up..."
rm -rf temp_guweb

echo "Step 4: Creating data directories..."
mkdir -p .data/avatars
mkdir -p .data/banners
mkdir -p .data/backgrounds

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Configure environment variables in the root .env file"
echo "2. Build the Docker images: docker compose build guweb"
echo "3. Start the services: docker compose up bancho mysql redis guweb"
echo ""
echo "Or use the Makefile commands:"
echo "- make build-guweb"
echo "- make run-with-guweb"
echo ""
echo "For more details, see guweb/INSTALL.md"
echo ""
