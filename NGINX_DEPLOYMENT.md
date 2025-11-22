# NGINX 部署与 HTTPS 配置指南

本文档记录当前环境的 nginx 部署步骤、证书申请方式，以及针对三个域名的反向代理与 HTTPS 配置。域名如下：(这是我的域名，到时候自己换)

- suagent.jehol-ppx.com
- api.jehol-ppx.com
- mcp.jehol-ppx.com

## 1. 前置条件

- 系统已安装 Docker、docker compose（项目本身已在运行）。
- 域名 DNS A 记录已指向服务器公网 IP（你的服务器公网IP）。
- 服务器已开放 80/443 端口。
- 用户：ubuntu。

## 2. 安装 nginx 以及 acme.sh

```bash
# nginx
sudo apt update && sudo apt install -y nginx
# acme.sh
curl https://get.acme.sh | sh -s email=your-email@example.com
```

## 3. 准备目录与权限

```bash
# ACME 验证目录
sudo mkdir -p /var/www/acme
sudo chown ubuntu:ubuntu /var/www/acme

# 证书目录
sudo mkdir -p /etc/nginx/ssl
sudo chown ubuntu:ubuntu /etc/nginx/ssl
```

## 4. 使用 acme.sh 申请多域名 ECC 证书（HTTP-01 / webroot）

```bash
~/.acme.sh/acme.sh --issue \
  -d suagent.jehol-ppx.com \
  -d api.jehol-ppx.com \
  -d mcp.jehol-ppx.com \
  -w /var/www/acme \
  --keylength ec-256
```

## 5. 安装证书并配置续期自动重载 nginx

```bash
~/.acme.sh/acme.sh --install-cert -d suagent.jehol-ppx.com \
  --key-file /etc/nginx/ssl/suagent.jehol-ppx.com.key \
  --fullchain-file /etc/nginx/ssl/suagent.jehol-ppx.com.fullchain.cer \
  --reloadcmd "sudo systemctl reload nginx"
```

说明：acme.sh 会在证书续期后自动执行 reload 命令，无需手动续期。

## 6. nginx 配置（/etc/nginx/sites-available/default）

核心逻辑：
- 80 端口：仅保留 `/.well-known/acme-challenge/` 静态处理，其余 301 跳转到 HTTPS。
- 443 端口：
  - `suagent.jehol-ppx.com` → `http://127.0.0.1:11451`
  - `api.jehol-ppx.com/suagent/` → `http://127.0.0.1:8000/`
  - `mcp.jehol-ppx.com/youtube/sse` → `http://127.0.0.1:10086/sse`（SSE/CORS/长超时/禁缓冲），其它路径 → `http://127.0.0.1:10086`

示例配置（已应用）：

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

# ---- HTTP (port 80) redirect to HTTPS, keep ACME ----
server {
    listen 80;
    listen [::]:80;
    server_name suagent.jehol-ppx.com;

    location ^~ /.well-known/acme-challenge/ {
        root /var/www/acme;
        default_type text/plain;
        try_files $uri =404;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name api.jehol-ppx.com;

    location ^~ /.well-known/acme-challenge/ {
        root /var/www/acme;
        default_type text/plain;
        try_files $uri =404;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name mcp.jehol-ppx.com;

    location ^~ /.well-known/acme-challenge/ {
        root /var/www/acme;
        default_type text/plain;
        try_files $uri =404;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# catch-all
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    return 404;
}

# ---- HTTPS (port 443) ----
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name suagent.jehol-ppx.com;
    ssl_certificate /etc/nginx/ssl/suagent.jehol-ppx.com.fullchain.cer;
    ssl_certificate_key /etc/nginx/ssl/suagent.jehol-ppx.com.key;

    location / {
        proxy_pass http://127.0.0.1:11451;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.jehol-ppx.com;
    ssl_certificate /etc/nginx/ssl/suagent.jehol-ppx.com.fullchain.cer;
    ssl_certificate_key /etc/nginx/ssl/suagent.jehol-ppx.com.key;

    location = /suagent {
        return 301 /suagent/;
    }

    location /suagent/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }

    location / {
        return 404;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name mcp.jehol-ppx.com;
    ssl_certificate /etc/nginx/ssl/suagent.jehol-ppx.com.fullchain.cer;
    ssl_certificate_key /etc/nginx/ssl/suagent.jehol-ppx.com.key;

    location /youtube/sse {
        proxy_pass http://127.0.0.1:10086/sse;

        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
        keepalive_timeout 86400s;
        proxy_next_upstream off;
        add_header Content-Type 'text/event-stream';
        add_header Cache-Control 'no-cache';
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type' always;
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    location / {
        proxy_pass http://127.0.0.1:10086;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

## 7. 检查并重载 nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 8. 验证

- HTTP 自动跳转至 HTTPS。
- 三个域名证书有效（浏览器或 `curl -I https://suagent.jehol-ppx.com` 等查看）。
- SSE 测试（注意 SSE 长连接会超时退出，这是正常现象）：  
  `curl -N --resolve mcp.jehol-ppx.com:443:127.0.0.1 https://mcp.jehol-ppx.com/youtube/sse`

## 9. 续期

acme.sh 默认在 `~/.acme.sh` 的 cron 中自动续期。续期后会执行 `sudo systemctl reload nginx`，无需额外操作。若需手动续期，可执行：

```bash
~/.acme.sh/acme.sh --renew -d suagent.jehol-ppx.com --force
```

