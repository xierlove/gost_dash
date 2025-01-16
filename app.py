from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import platform
import subprocess
import os
import json

app = Flask(__name__)
app.secret_key = 'xierlove'  # 请更改为一个强密码

# 初始化认证
auth = HTTPBasicAuth()

# 设置用户名和密码
users = {
    "xierlove": generate_password_hash("xierlove")  # 请更改为你想要的用户名和密码
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# 定义规则存储文件路径
RULES_FILE = '/opt/gost_web/rules.json'

# HTML 模板包含在 Python 字符串中
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>xierlove 转发配置</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* Resetting default margin and padding */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f4f8; /* 浅色背景 */
            color: #333;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: space-between;
            padding: 30px;
            overflow: hidden; /* 防止内容溢出 */
        }

        .form-container, .rules-container {
            width: 48%;
            background: #ffffff;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease-in-out;
            border: 1px solid #e0e4e8; /* 边框 */
            overflow: hidden;
        }

        .form-container:hover, .rules-container:hover {
            transform: translateY(-5px);
        }

        h1 {
            text-align: center;
            font-size: 2rem;
            margin-bottom: 15px;
            color: #495057;
        }

        h2 {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #495057;
        }

        p {
            font-size: 1rem;
            color: #6c757d;
            text-align: center;
            margin-top: 20px;
        }

        form label {
            font-size: 1rem;
            color: #495057;
            margin-top: 15px;
            display: block;
        }

        form input,
        form select {
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            border-radius: 8px;
            border: 1px solid #ddd;
            box-sizing: border-box;
            font-size: 1rem;
            background-color: #f8f9fa;
            transition: border-color 0.3s ease;
            word-wrap: break-word; /* 防止长文字溢出 */
        }

        form input:focus,
        form select:focus {
            border-color: #007bff;
            outline: none;
            background-color: #ffffff;
        }

        button {
            padding: 12px 20px;
            background-color: #3498db;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }

        button:hover {
            background-color: #218838;
            transform: translateY(-3px);
        }

        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 6px;
            font-size: 1rem;
        }

        .alert.success {
            background-color: #d4edda;
            color: #155724;
        }

        .alert.danger {
            background-color: #f8d7da;
            color: #721c24;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
            table-layout: fixed; /* 保证表格内容不会溢出 */
        }

        table th,
        table td {
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
            word-wrap: break-word; /* 防止长文字溢出 */
        }

        table th {
            background-color: #f8f9fa;
            color: #495057;
        }

        table tr:hover {
            background-color: #f1f1f1;
            transition: background-color 0.3s;
        }

        .delete-button {
            background-color: #dc3545;
            color: white;
            border: none;
            padding: 8px 15px;
            cursor: pointer;
            border-radius: 6px;
            font-size: 1rem;
            transition: background-color 0.3s, transform 0.2s ease;
        }

        .delete-button:hover {
            background-color: #c82333;
            transform: translateY(-2px);
        }

        .delete-button:focus {
            outline: none;
        }

        /* Media Queries for smaller screens */
        @media (max-width: 992px) {
            .container {
                flex-direction: column;
                align-items: center;
            }

            .form-container, .rules-container {
                width: 90%;
            }
        }

        /* Prevent table content overflow */
        table td,
        table th {
            max-width: 200px; /* 限制单元格最大宽度 */
            overflow: hidden;
            text-overflow: ellipsis; /* 显示省略号 */
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-container">
            <h1>xierlove 转发配置</h1>
            <p>当前操作系统：{{ os_type }}</p>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert {{ category }}">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <h2>创建新的转发规则</h2>
            <form method="POST">
                <label for="protocol">协议:</label>
                <select id="protocol" name="protocol" required>
                    <option value="tcp">TCP</option>
                    <option value="udp">UDP</option>
                    <option value="http">HTTP</option>
                    <option value="https">HTTPS</option>
                </select>

                <label for="local_addr">本地地址:</label>
                <input type="text" id="local_addr" name="local_addr" value="0.0.0.0" required>

                <label for="local_port">本地端口:</label>
                <input type="number" id="local_port" name="local_port" value="8080" required>

                <label for="remote_addr">远程地址:</label>
                <input type="text" id="remote_addr" name="remote_addr" value="127.0.0.1" required>

                <label for="remote_port">远程端口:</label>
                <input type="number" id="remote_port" name="remote_port" value="80" required>

                <button type="submit">添加规则</button>
            </form>
        </div>

        <div class="rules-container">
            <h2>现有转发规则</h2>
            {% if rules %}
                <table>
                    <tr>
                        <th>ID</th>
                        <th>协议</th>
                        <th>本地地址:端口</th>
                        <th>远程地址:端口</th>
                        <th>操作</th>
                    </tr>
                    {% for rule in rules %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td>{{ rule.protocol.upper() }}</td>
                            <td>{{ rule.local_addr }}:{{ rule.local_port }}</td>
                            <td>{{ rule.remote_addr }}:{{ rule.remote_port }}</td>
                            <td>
                                <form method="POST" action="{{ url_for('delete_rule', rule_id=loop.index0) }}">
                                    <button type="submit" class="delete-button">删除</button>
                                </form>
                            </td>
                        </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p>暂无转发规则。</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

def detect_os():
    """
    检测当前操作系统类型。
    """
    try:
        # 尝试使用 /etc/os-release 文件获取更详细信息
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release') as f:
                lines = f.readlines()
            os_info = {}
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    os_info[key] = value.strip('"')
            if 'ID' in os_info:
                return os_info['ID']
    except Exception as e:
        print(f"检测操作系统时出错: {e}")
    return 'unknown'

def load_rules():
    """
    从 JSON 文件加载规则。
    """
    if not os.path.exists(RULES_FILE):
        return []
    with open(RULES_FILE, 'r') as f:
        try:
            rules = json.load(f)
            return rules
        except json.JSONDecodeError:
            return []

def save_rules(rules):
    """
    将规则保存到 JSON 文件。
    """
    with open(RULES_FILE, 'w') as f:
        json.dump(rules, f, indent=4)

def update_gost_service(rules):
    """
    根据当前规则生成 systemd 服务文件并重启 GOST 服务。
    """
    try:
        if not rules:
            # 如果没有规则，停止并禁用 GOST 服务
            subprocess.run(['systemctl', 'stop', 'gost'], check=True)
            subprocess.run(['systemctl', 'disable', 'gost'], check=True)
            return

        # 构建 GOST 命令
        gost_path = '/usr/local/bin/gost/gost'  # 根据实际安装路径调整
        cmd = [gost_path]
        for rule in rules:
            cmd.extend(['-L', f"{rule['protocol']}://:{rule['local_port']}/{rule['remote_addr']}:{rule['remote_port']}"]) 

        # 创建 systemd 服务文件内容
        service_content = f"""
[Unit]
Description=GOST Service
After=network.target

[Service]
ExecStart={' '.join(cmd)}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
        service_path = '/etc/systemd/system/gost.service'
        with open(service_path, 'w') as service_file:
            service_file.write(service_content)

        # 重新加载 systemd 并启动 GOST 服务
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        subprocess.run(['systemctl', 'enable', 'gost'], check=True)
        subprocess.run(['systemctl', 'restart', 'gost'], check=True)

    except Exception as e:
        print(f"更新 GOST 服务时出错: {e}")

@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def index():
    os_type = detect_os()
    rules = load_rules()

    if request.method == 'POST':
        # 获取表单数据
        protocol = request.form.get('protocol', 'tcp').lower()
        local_addr = request.form.get('local_addr', '127.0.0.1').strip()
        local_port = request.form.get('local_port', '8080').strip()
        remote_addr = request.form.get('remote_addr', 'example.com').strip()
        remote_port = request.form.get('remote_port', '80').strip()

        # 简单验证
        if not (protocol and local_addr and local_port and remote_addr and remote_port):
            flash('所有字段都是必填的。', 'danger')
            return redirect(url_for('index'))

        # 验证端口是否为数字
        if not (local_port.isdigit() and remote_port.isdigit()):
            flash('端口必须是数字。', 'danger')
            return redirect(url_for('index'))

        # 添加新规则
        new_rule = {
            'protocol': protocol,
            'local_addr': local_addr,
            'local_port': local_port,
            'remote_addr': remote_addr,
            'remote_port': remote_port
        }
        rules.append(new_rule)
        save_rules(rules)
        update_gost_service(rules)
        flash('规则添加成功！', 'success')
        return redirect(url_for('index'))

    # 渲染内嵌的 HTML 模板
    return render_template_string(HTML_TEMPLATE, os_type=os_type, rules=rules)

@app.route('/delete/<int:rule_id>', methods=['POST'])
@auth.login_required
def delete_rule(rule_id):
    rules = load_rules()
    if 0 <= rule_id < len(rules):
        removed_rule = rules.pop(rule_id)
        save_rules(rules)
        update_gost_service(rules)
        flash('规则删除成功！', 'success')
    else:
        flash('无效的规则 ID。', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 以 root 用户运行以便管理 systemd 服务
    if os.geteuid() != 0:
        print("请以 root 用户运行此应用。")
        exit(1)
    app.run(host='0.0.0.0', port=5000)
