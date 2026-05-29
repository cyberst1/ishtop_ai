"""All Uzbek user-facing strings live here. Bot uses ONLY this dict."""
from __future__ import annotations

T = {
    # ---------- General ----------
    "app_name": "ISH TOP AI",
    "loading": "⏳ Yuklanmoqda...",
    "error_generic": "⚠️ Xatolik yuz berdi. Birozdan keyin urinib ko‘ring.",
    "blocked": "🚫 Sizning hisobingiz bloklangan. Admin bilan bog‘laning.",
    "rate_limited": "⏱ Juda tez yubormoqdasiz. Biroz kuting.",
    "back": "⬅️ Orqaga",
    "cancel": "❌ Bekor qilish",
    "yes": "✅ Ha",
    "no": "❌ Yo‘q",

    # ---------- /start ----------
    "start_welcome": (
        "👋 *ISH TOP AI*\n\n"
        "🇺🇿 O‘zbekistondagi barcha ish platformalaridan AI orqali ish yoki "
        "xodim topib beradi.\n\n"
        "🪙 *Har bir e'lon ochish:* 2 coin\n\n"
        "🎁 Sizga *4 coin* BEPUL berildi.\n"
        "(2 ta e'lon ochish uchun)"
    ),

    # ---------- Main menu ----------
    "btn_search": "🔍 Ish qidirish",
    "btn_earn": "🪙 Coin ishlash",
    "btn_plans": "⭐ Tariflar",
    "btn_profile": "👤 Profil",
    "btn_help": "ℹ️ Yordam",
    "btn_advisor": "🧠 AI Career Advisor",

    # ---------- Search flow ----------
    "search_who_are_you": "🧠 Siz kimsiz?",
    "btn_role_jobseeker": "👨‍💻 Ish qidiryapman",
    "btn_role_employer": "🏢 Ish beruvchiman",
    "search_query_prompt": (
        "💬 *Qanday ish izlayapsiz?*\n\n"
        "Misol uchun:\n"
        "• Python dasturchi\n"
        "• Grafik dizayner\n"
        "• SMM manager\n"
        "• Remote frontend developer"
    ),
    "search_searching": "🔎 AI yordamida qidirilmoqda...",
    "search_no_results": "😔 Hech narsa topilmadi. Boshqacha so‘rov bilan urinib ko‘ring.",
    "search_daily_limit": (
        "📵 *Kunlik limit tugadi.*\n\n"
        "Free tarifda kuniga {limit} ta qidiruv. Premium oling — cheksiz qidiruv."
    ),
    "search_off_topic": (
        "🤖 *ISH TOP AI* faqat *ish, karyera, kasb* mavzularida yordam beradi.\n\n"
        "Hazil, suhbat yoki boshqa mavzular qabul qilinmaydi."
    ),

    # ---------- Job card ----------
    "btn_job_details": "📄 Batafsil",
    "btn_job_contact": "📞 Aloqa",
    "btn_job_save": "❤️ Saqlash",
    "btn_job_next": "⏭ Keyingi",
    "btn_job_unlock": "🔓 Ochish (2 coin)",
    "job_locked_preview": (
        "🔒 *E'lon yopiq*\n\n"
        "Ushbu e'lonni ochish uchun *2 coin* sarflanadi.\n"
        "Balansingiz: *{balance}* coin"
    ),
    "job_insufficient_coins": (
        "🪙 *Coin yetarli emas.*\n\n"
        "Sizda: *{balance}* coin\n"
        "Kerak: *2* coin\n\n"
        "Coin ishlash uchun «🪙 Coin ishlash» bo‘limiga kiring."
    ),
    "job_unlocked": "✅ E'lon ochildi!",
    "job_saved": "❤️ Saqlandi!",

    # ---------- Profile ----------
    "profile_card": (
        "👤 *Sizning profilingiz*\n\n"
        "🪙 Coin: *{balance}*\n"
        "⭐ Tarif: *{plan}*\n"
        "📅 Bugungi qidiruvlar: *{searches_today}*\n"
        "👥 Referrallar: *{referrals}*\n"
        "❤️ Saqlangan: *{saved}*"
    ),

    # ---------- Plans ----------
    "plans_header": "⭐ *Tariflar*",
    "plan_free": (
        "*FREE — 0 so‘m*\n"
        "• AI ish qidiruvi\n"
        "• Coin orqali ochish\n"
        "• Kuniga 3 ta qidiruv"
    ),
    "plan_premium": (
        "*PREMIUM — 9 000 so‘m*\n"
        "• Cheksiz qidiruv\n"
        "• AI search\n"
        "• Coin ochish"
    ),
    "plan_premium_plus": (
        "*PREMIUM+ — 19 990 so‘m*\n"
        "• Cheksiz qidiruv\n"
        "• AI search\n"
        "• Coin ochish\n"
        "• AI Career Advisor"
    ),
    "btn_buy_premium": "💳 Premium sotib olish",
    "btn_buy_premium_plus": "💎 Premium+ sotib olish",

    # ---------- Earn / Bonus ----------
    "earn_header": (
        "🪙 *Coin ishlash usullari*\n\n"
        "1. 👥 Do‘st taklif qilish\n"
        "2. 🎁 Bonus kanallarga qo‘shilish"
    ),
    "btn_invite": "👥 Do‘st taklif qilish",
    "btn_bonus_channels": "🎁 Bonus kanallar",
    "invite_card": (
        "👥 *Do‘st taklif qilish*\n\n"
        "🎁 1-do‘st: *+2 coin*\n"
        "🎁 Keyingi har biri: *+1 coin*\n\n"
        "Sizning havolangiz:\n`{link}`\n\n"
        "Taklif qilingan: *{count}* kishi"
    ),
    "bonus_channels_header": "🎁 *Bonus kanallar* — har biri uchun *+0.5 coin*",
    "bonus_join_btn": "🔗 Qo‘shilish",
    "bonus_check_btn": "✅ Tekshirish",
    "bonus_already_claimed": "Bu kanal uchun bonus allaqachon olingan.",
    "bonus_not_subscribed": "❌ Hali kanalga qo‘shilmagansiz.",
    "bonus_rewarded": "🎉 +0.5 coin qo‘shildi!",

    # ---------- Help ----------
    "help_text": (
        "ℹ️ *Yordam*\n\n"
        "🔍 *Ish qidirish* — AI yordamida vakansiyalar\n"
        "🪙 *Coin ishlash* — referral va bonus kanallar\n"
        "⭐ *Tariflar* — Free / Premium / Premium+\n"
        "👤 *Profil* — balans, tarif, statistika\n\n"
        "Savol bo‘lsa: @support"
    ),

    # ---------- Advisor ----------
    "advisor_only_premium_plus": (
        "💎 *AI Career Advisor* faqat *Premium+* foydalanuvchilar uchun.\n\n"
        "⭐ Tariflar bo‘limiga o‘tib obunani faollashtiring."
    ),
    "advisor_prompt": (
        "🧠 *AI Career Advisor*\n\n"
        "Karyera, ko‘nikma, roadmap, maosh, intervyu yoki freelancing haqida so‘rang."
    ),

    # ---------- Admin ----------
    "admin_not_allowed": "⛔ Sizda admin huquqi yo‘q.",
    "admin_password_prompt": "🔐 Admin paroli kiriting:",
    "admin_password_wrong": "❌ Parol noto‘g‘ri.",
    "admin_login_ok": "✅ Admin panelga xush kelibsiz.",
    "admin_session_expired": "⏰ Admin sessiyasi tugadi. Qayta kiring: /admin_kirish",
    "admin_panel_title": "🎛 *Admin panel*",
    "btn_admin_users": "👥 Userlar",
    "btn_admin_blocks": "🚫 Block System",
    "btn_admin_plans": "⭐ Tariflar",
    "btn_admin_balance": "🪙 Balans",
    "btn_admin_bonus": "🎁 Bonus Kanallar",
    "btn_admin_broadcast": "📢 Xabar Yuborish",
    "btn_admin_stats": "📊 Statistika",
    "btn_admin_settings": "⚙️ Sozlamalar",
    "btn_admin_security": "🛡 Security",
    "btn_admin_logs": "📂 Loglar",

    # ---------- Plans names ----------
    "plan_name_free": "Free",
    "plan_name_premium": "Premium",
    "plan_name_premium_plus": "Premium+",
}
