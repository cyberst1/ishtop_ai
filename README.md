# 🤖 ISH TOP AI

> **AI Career Operating System** — O‘zbekistondagi barcha ish platformalaridan AI orqali ish yoki xodim topib beruvchi premium Telegram bot.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0.svg)](https://aiogram.dev)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()

---

## ✨ Nima u?

**ISH TOP AI** — oddiy ish boti emas. Bu AI quvvatidagi karyera platformasi:

- 🔍 Ish e'lonlarini **HH.uz, OLX, Jooble, LinkedIn, Indeed, Telegram kanallari**dan yig‘adi
- 🧠 **Semantik niyatni** tushunadi (sinonim, remote, daraja, maosh)
- 🪙 **Coin iqtisodiyoti** (1 ta e'lon = 2 coin, ro‘yxatdan o‘tishda 4 coin sovg‘a)
- ⭐ **Free / Premium / Premium+** tariflar
- 👥 **Referral dasturi** abuse himoyasi bilan
- 🎁 Har bir bonus kanal uchun **+0.5 coin**
- 🛡 **20+ kiberxavfsizlik qatlami**
- 🎛 To‘liq **admin panel** — `/admin_kirish`

AI **faqat karyera bilan bog‘liq** savollarga javob beradi. Hazil, siyosat, suhbat — `IntentGuard` tarafidan rad etiladi (LLM ham chaqirilmaydi → xarajat tejaladi).

---

## 🏗 Tech Stack

| Qatlam | Tanlov |
|---|---|
| Til | Python 3.11+ |
| Framework | aiogram 3.x (async) |
| DB | SQLite + aiosqlite |
| Scheduler | APScheduler |
| HTTP | aiohttp + BeautifulSoup4 |
| AI | NVIDIA NIM API (OpenAI-compatible) |
| Security | bcrypt, HMAC, secrets |
| Deploy | Docker, Render, Railway, VPS+nginx |

---

## 📂 Loyiha tuzilishi

```
app/
├── main.py              # entrypoint
├── config/              # pydantic settings
├── database/            # schema + repositories (13 jadval)
├── bot/                 # dispatcher, FSM, lifecycle
├── middlewares/         # antiflood, throttle, ban, logging
├── keyboards/           # UI klaviaturalar (Uzbek)
├── handlers/            # user + admin handlerlari
├── services/            # coin, referral, subscription, search, advisor
├── parsers/             # 6 ta job board parseri
├── ai/                  # NVIDIA client, intent guard, promptlar
├── security/            # rate limit, bcrypt, sanitizer, abuse
├── cache/               # TTL cache
├── utils/               # logger, text, validators
└── locales/uz.py        # barcha O‘zbek matnlar
```

---

## 🚀 Tezkor ishga tushirish

```bash
git clone https://github.com/cyberst1/ishtop_ai.git
cd ishtop_ai

# 1. Kutubxonalar
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Sozlash
cp .env.example .env
# .env tahrirlang: BOT_TOKEN, ADMIN_IDS, ADMIN_PASSWORD_HASH, NVIDIA_API_KEY

# 3. DB ishga tushirish
python -m app.database.engine

# 4. Botni yoqish (polling)
python -m app.main
```

### Docker

```bash
docker compose up -d --build
```

---

## 🪙 Coin iqtisodiyoti

| Hodisa | Coin |
|---|---|
| Ro‘yxatdan o‘tish sovg‘asi | **+4** |
| Ish e'lonini ochish | **−2** |
| 1-referral | **+2** |
| Keyingi har bir referral | **+1** |
| Bonus kanal qo‘shilish | **+0.5** |

---

## ⭐ Tariflar

| Tarif | Narx | Kunlik qidiruv | AI search | Career Advisor |
|---|---|---|---|---|
| Free | 0 | 3 | ✅ | ❌ |
| Premium | 9 000 so‘m | ∞ | ✅ | ❌ |
| Premium+ | 19 990 so‘m | ∞ | ✅ | ✅ |

---

## 🛡 20 ta xavfsizlik qatlami

1. Per-user rate limiting (token bucket)
2. AntiFlood middleware (sliding window)
3. Anti-spam content filter
4. Faqat parametrli SQL (SQLi himoya)
5. HMAC-imzolangan callback data
6. MarkdownV2 escaping
7. Admin sessiya tugashi (30 daqiqa)
8. ADMIN_IDS allowlist + bcrypt parol
9. Bot token faqat `.env`da
10. Input sanitization (uzunlik, charset)
11. Har bir parserda HTTP timeout
12. Parser concurrency cap + cooldown
13. Strukturali JSON logging
14. Global error handler
15. Action cooldownlar (search: 5s, AI: 10s)
16. Referral abuse himoyasi
17. Multi-account aniqlash
18. Cache poisoning himoyasi
19. `.env` git'ga tushmaydi
20. Bcrypt admin parol (cost 12)

---

## 🧠 AI Intent Guard

Bot **karyeradan tashqari** savollarni rad etadi. Off-topic bo‘lsa LLM chaqirilmaydi.

---

## 🎛 Admin Panel

`/admin_kirish` → ADMIN_IDS tekshiruvi → bcrypt parol → sessiya.

**Tugmalar:** 👥 Userlar · 🚫 Block · ⭐ Tariflar · 🪙 Balans · 🎁 Bonus Kanallar · 📢 Xabar · 📊 Statistika · ⚙️ Sozlamalar · 🛡 Security · 📂 Loglar

---

## 🌐 Deployment

[`deploy/DEPLOYMENT.md`](deploy/DEPLOYMENT.md) — Render, Railway, Docker, VPS+nginx.

---

## 📈 Scaling

- **0–10k user:** SQLite + polling, 1 VPS
- **10k–100k:** Postgres + Redis FSM + nginx webhook
- **100k+:** read replicalar, parser worker'lar alohida konteynerda

---

## 📜 Litsenziya

Proprietary. Barcha huquqlar himoyalangan.
