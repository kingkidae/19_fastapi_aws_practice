#!/usr/bin/env bash
# EC2(Amazon Linux 2023 / Ubuntu)에서 실행: bash ~/app/deploy/setup.sh
# 처음 설치와 코드 업데이트 모두 이 스크립트 하나로 한다.
set -euo pipefail
cd "$(dirname "$0")/.."
APP_DIR="$(pwd)"

command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv sync --frozen --no-dev  # .python-version의 파이썬까지 uv가 받아온다

sudo tee /etc/systemd/system/stock.service >/dev/null <<EOF
[Unit]
Description=stock board (FastAPI)
After=network-online.target
Wants=network-online.target

[Service]
User=$(whoami)
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 80
# root가 아니어도 80번 포트를 쓸 수 있게
AmbientCapabilities=CAP_NET_BIND_SERVICE
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable stock
sudo systemctl restart stock
sleep 2
curl -fsS -o /dev/null http://localhost/ && echo "실행 중: http://$(curl -fsS https://checkip.amazonaws.com)/"
