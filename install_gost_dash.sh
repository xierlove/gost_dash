#!/bin/bash

# 确保脚本以 root 用户运行
if [ "$EUID" -ne 0 ]
  then echo "请以 root 用户运行此脚本。"
  exit
fi

# 定义变量
PROJECT_DIR="/opt/gost_web"
APP_PY_URL="https://raw.githubusercontent.com/xierlove/gost_dash/refs/heads/main/app.py"
GOST_VERSION="v2.11.1"  # 你可以根据需要更改版本
GOST_FILE="gost-linux-amd64-${GOST_VERSION}.gz"
GOST_URL="https://github.com/ginuerzh/gost/releases/download/${GOST_VERSION}/${GOST_FILE}"
RULES_FILE="${PROJECT_DIR}/rules.json"
SERVICE_FILE="/etc/systemd/system/gost_web.service"

# 更新系统
echo "更新系统软件包..."
apt-get update -y && apt-get upgrade -y

# 安装必要的软件包
echo "安装必要的软件包..."
apt-get install -y python3 python3-pip git curl ufw

# 安装 Python 依赖包
echo "安装 Python 依赖包..."
pip3 install Flask Flask-HTTPAuth

# 创建项目目录
echo "创建项目目录 $PROJECT_DIR ..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 下载 app.py
echo "下载 app.py 从 $APP_PY_URL ..."
curl -s -o app.py $APP_PY_URL
if [ $? -ne 0 ]; then
    echo "下载 app.py 失败，请检查 URL 或网络连接。"
    exit 1
fi

# 设置 app.py 的权限
chmod 644 app.py

# 下载 GOST
echo "创建 GOST 目录 /usr/local/bin/gost ..."
mkdir -p /usr/local/bin/gost
cd /usr/local/bin/gost

echo "下载 GOST 从 $GOST_URL ..."
wget -q $GOST_URL
if [ $? -ne 0 ]; then
    echo "下载 GOST 失败，请检查版本号或网络连接。"
    exit 1
fi

# 解压 GOST
echo "解压 GOST..."
gunzip -f $GOST_FILE
if [ $? -ne 0 ]; then
    echo "解压 GOST 失败。"
    exit 1
fi

# 重命名 GOST
GOST_BINARY="gost"
mv gost-linux-amd64-${GOST_VERSION} $GOST_BINARY

# 赋予执行权限
chmod +x $GOST_BINARY

# 创建符号链接
ln -sf /usr/local/bin/gost/gost /usr/local/bin/gost

# 返回项目目录
cd $PROJECT_DIR

# 创建空的 rules.json 文件
if [ ! -f "$RULES_FILE" ]; then
    echo "创建空的 rules.json 文件..."
    echo "[]" > $RULES_FILE
fi

# 创建 systemd 服务文件
echo "创建 systemd 服务文件 $SERVICE_FILE ..."
cat > $SERVICE_FILE <<EOL
[Unit]
Description=GOST Web Interface
After=network.target

[Service]
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# 重新加载 systemd
echo "重新加载 systemd 守护进程..."
systemctl daemon-reload

# 启用并启动 gost_web 服务
echo "启用并启动 gost_web 服务..."
systemctl enable gost_web
systemctl start gost_web

# 检查服务状态
echo "检查 gost_web 服务状态..."
systemctl status gost_web --no-pager

# 配置防火墙
echo "配置防火墙规则..."
ufw allow 5000/tcp
ufw allow 22/tcp  # 确保允许 SSH 连接
echo "y" | ufw enable

echo "安装完成。请访问 http://<服务器IP>:5000"
