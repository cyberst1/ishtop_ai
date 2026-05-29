# 🚀 ISH TOP AI — Deployment Guide

To‘rtta deploy varianti: **Docker Compose**, **VPS + nginx**, **Render**, **Railway**.

---

## 0. Tayyorgarlik (har xil deploy uchun bir xil)

```bash
# 1) Bot yarating
@BotFather → /newbot → BOT_TOKEN ni saqlang

# 2) NVIDIA API kalit (https://build.nvidia.com)
NVIDIA_API_KEY=nvapi-...

# 3) Admin parol hash
python -c "import bcrypt; print(bcrypt.hashpw(b'YOUR_STRONG_PASSWORD', bcrypt.gensalt(12)).decode())"

# 4) HMAC sirini generatsiya qiling
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

`.env` faylini `.env.example` asosida tayyorlang.

---

## 1. Docker Compose (eng oson)

```bash
git clone https://github.com/cyberst1/ishtop_ai.git
cd ishtop_ai
cp .env.example .env
# .env tahrirlang

docker compose up -d --build
docker compose logs -f bot
```

DB avtomatik `data/ish_top_ai.db` ichida saqlanadi (volume).

---

## 2. VPS (Ubuntu 22.04+) + nginx + HTTPS

### 2.1 System

```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx git
```

### 2.2 Application

```bash
git clone https://github.com/cyberst1/ishtop_ai.git /opt/ishtop_ai
cd /opt/ishtop_ai
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env: MODE=webhook, WEBHOOK_URL=https://yourdomain.uz/webhook, WEBHOOK_SECRET=...
python -m app.database.engine
```

### 2.3 systemd service

`/etc/systemd/system/ishtop-ai.service`:

```ini
[Unit]
Description=ISH TOP AI Telegram bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ishtop_ai
EnvironmentFile=/opt/ishtop_ai/.env
ExecStart=/opt/ishtop_ai/.venv/bin/python -m app.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ishtop-ai
sudo journalctl -u ishtop-ai -f
```

### 2.4 nginx + HTTPS

`/etc/nginx/sites-available/ishtop-ai`: ko‘ring [`nginx.conf`](nginx.conf).

```bash
sudo ln -s /etc/nginx/sites-available/ishtop-ai /etc/nginx/sites-enabled/
sudo certbot --nginx -d yourdomain.uz
sudo systemctl reload nginx
```

Webhook aktivatsiyasi bot startup paytida avtomatik.

---

## 3. Render (free tier ham mavjud)

1. **New → Web Service → from GitHub**
2. Repo: `cyberst1/ishtop_ai`
3. Build: `pip install -r requirements.txt`
4. Start: `python -m app.main`
5. **Environment** tab — `.env` o‘zgaruvchilarni qo‘shing.
6. `MODE=webhook`, `WEBHOOK_URL=https://your-render-app.onrender.com/webhook`
7. Deploy.

---

## 4. Railway

```bash
railway login
railway init
railway up
```

Yoki UI orqali:
1. **New Project → Deploy from GitHub**
2. Variables: `.env` ni nusxa ko‘chiring
3. `MODE=webhook`, `WEBHOOK_URL=https://${{RAILWAY_STATIC_URL}}/webhook`

---

## 5. Webhook vs Polling

| Mode | Tezlik | Resurs | Tavsiya |
|---|---|---|---|
| polling | ~1-3s | yuqori CPU | Dev / kichik trafik |
| webhook | <300ms | past | **Production (>1k user)** |

`MODE=polling` → bir VPS yetarli.
`MODE=webhook` → nginx + HTTPS + qayta ishlovchi `WEBHOOK_SECRET` kerak.

---

## 6. Backup

```bash
# Daily SQLite backup cron
0 3 * * * cp /opt/ishtop_ai/data/ish_top_ai.db \
          /opt/ishtop_ai/data/backup-$(date +\%F).db
```

---

## 7. Monitoring

- `journalctl -u ishtop-ai -f` — real-time log
- `tail -f data/logs/bot.log | jq .` — JSON logs
- Sentry / Bugsnag integratsiya qilishingiz mumkin (`logging_mw.py` ichida)

---

## 8. Scaling roadmap

| Stage | Users | Stack |
|---|---|---|
| 1 | 0–10k | SQLite + 1 VPS + polling |
| 2 | 10k–100k | Postgres + Redis FSM + nginx webhook |
| 3 | 100k+ | Read replicas, parser worker konteynerlar, NATS/Redis Streams |
