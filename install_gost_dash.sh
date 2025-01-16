#!/bin/bash

# 一键安装脚本：搭建可视化的 GOST 转发网页

# 如果脚本遇到错误则退出
set -e

# 变量定义
APP_DIR="/opt/gost_web"
APP_URL="https://raw.githubusercontent.com/xierlove/gost_dash/main/app.py"
APP_FILE="$APP_DIR/app.py"
RULES_FILE="$APP_DIR/rules.json"
GOST_DIR="/usr/local/bin/gost"
GOST_URL="https://github.com/ginuerzh/gost/releases/download/v2.11.1/gost-linux-amd64-2.11.1.gz"
GOST_BINARY="gost"
SYSTEMD_SERVICE="/etc/systemd/system/gost_web.service"
FLASK_PORT=5000
SECRET_KEY="your_secret_key"  # 请在下载后手动更改为强密码
USERNAME="admin"              # 默认用户名
PASSWORD="your_password"      # 默认密码，请在下载后手动更改为强密码

# 检查是否以root用户运行
if [ "$EUID" -ne 0 ]; then
  echo "请以 root 用户运行此脚本。"
  exit 1
fi

# 更新系统软件包
echo "更新系统软件包..."
apt-get update -y
apt-get upgrade -y

# 安装必要的软件包
echo "安装必要的软件包..."
apt-get install -y python3 python3-pip git curl ufw

# 安装 Python 依赖
echo "安装 Python 依赖..."
pip3 install Flask Flask-HTTPAuth

# 安装 GOST
if [ ! -f "$GOST_DIR/gost" ]; then
    echo "安装 GOST..."
    mkdir -p "$GOST_DIR"
    cd "$GOST_DIR"
    wget "$GOST_URL"
    gunzip gost-linux-amd64-2.11.1.gz
    mv gost-linux-amd64-2.11.1 gost
    chmod +x gost
    echo "GOST 安装完成。"
else
    echo "GOST 已经安装，跳过。"
fi

# 创建项目目录
echo "创建项目目录..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# 下载 app.py
echo "下载 app.py..."
curl -o "$APP_FILE" "$APP_URL"

# 设置 SECRET_KEY 和认证信息
echo "配置 app.py 的 SECRET_KEY 和认证信息..."
# 使用sed替换secret_key、username和password
sed -i "s/your_secret_key/$SECRET_KEY/" "$APP_FILE"
sed -i "s/admin/$USERNAME/" "$APP_FILE"
sed -i "s/your_password/$PASSWORD/" "$APP_FILE"

# 确保 rules.json 存在
if [ ! -f "$RULES_FILE" ]; then
    echo "创建 rules.json 文件..."
    echo "[]" > "$RULES_FILE"
fi

# 创建 systemd 服务文件
echo "创建 systemd 服务文件..."
cat > "$SYSTEMD_SERVICE" <<EOF
[Unit]
Description=GOST Web Interface
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_FILE
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd 并启动服务
echo "重新加载 systemd 并启动服务..."
systemctl daemon-reload
systemctl enable gost_web
systemctl start gost_web

# 配置防火墙
echo "配置防火墙..."
ufw disable

echo "安装和配置完成。请访问 http://<服务器IP>:$FLASK_PORT 进行管理。"
echo "默认登录凭证："
echo "用户名: $USERNAME"
echo "密码: $PASSWORD"
