"""All Uzbek user-facing strings. Bot uses ONLY this dict."""
from __future__ import annotations

# `_` in @cybst_academy must be escaped in legacy Markdown, otherwise Telegram
# treats it as the start of an italic span and rejects the message with
# `Bad Request: can't parse entities`.
# We render it as a clickable Markdown link — the visible underscore is escaped
# inside the link text, the URL stays intact.
SUPPORT_PLAIN = "@cybst_academy"
SUPPORT_URL = "https://t.me/cybst_academy"
SUPPORT = f"[@cybst\\_academy]({SUPPORT_URL})"

T = {
    # ---------- General ----------
    "app_name": "ISH TOP AI",
    "support": SUPPORT,
    "loading": "⏳ Yuklanmoqda...",
    "error_generic": (
        "⚠️ Xatolik yuz berdi. Birozdan keyin urinib ko'ring.\n"
        f"Yordam: {SUPPORT}"
    ),
    "blocked": (
        "🚫 Sizning hisobingiz bloklangan.\n"
        f"Admin bilan bog'laning: {SUPPORT}"
    ),
    "rate_limited": "⏱ Juda tez yubormoqdasiz. Biroz kuting va qayta urinib ko'ring.",
    "back": "⬅️ Orqaga",
    "cancel": "❌ Bekor qilish",
    "yes": "✅ Ha",
    "no": "❌ Yo'q",

    # ---------- /start ----------
    "start_welcome": (
        "👋 *ISH TOP AI*ga xush kelibsiz!\n\n"
        "🇺🇿 O'zbekiston bo'ylab eng yaxshi ish va xodim topish AI yordamchisi.\n\n"
        "Bot 6 ta katta platformadan vakansiyalarni yig'adi:\n"
        "• HH.uz  • OLX.uz  • LinkedIn\n"
        "• Indeed  • Jooble  • Telegram kanallari\n\n"
        "💡 *Qanday ishlaydi?*\n"
        "1️⃣ «🔍 Ish qidirish» tugmasini bosasiz\n"
        "2️⃣ Qanday ish izlayotganingizni yozasiz\n"
        "3️⃣ AI 6 ta saytdan e'lonlarni yig'adi\n"
        "4️⃣ Bog'lanish ma'lumotlari *bepul* ko'rinadi 📞\n\n"
        "🪙 *Narx:* har bir qidiruv = *2 coin*\n"
        "(natija topilmasa coin yechilmaydi)\n\n"
        "🎁 *Sovg'a:* sizga *4 coin* BEPUL berildi\n"
        "(2 ta qidiruv qilishingiz uchun yetadi)\n\n"
        f"📩 Yordam kerakmi? {SUPPORT}"
    ),

    # ---------- Main menu ----------
    "btn_search": "🔍 Ish qidirish",
    "btn_earn": "🪙 Coin ishlash",
    "btn_plans": "⭐ Tariflar",
    "btn_profile": "👤 Profil",
    "btn_help": "ℹ️ Yordam",
    "btn_advisor": "🧠 AI Career Advisor",

    # ---------- Search flow ----------
    "search_who_are_you": (
        "🧠 *Siz kimsiz?*\n\n"
        "Quyidagilardan birini tanlang:"
    ),
    "btn_role_jobseeker": "👨‍💻 Ish qidiryapman",
    "btn_role_employer": "🏢 Ish beruvchiman",
    "search_query_prompt": (
        "💬 *Qanday ish izlayapsiz?*\n\n"
        "Misol uchun:\n"
        "• Python dasturchi\n"
        "• Grafik dizayner\n"
        "• SMM manager\n"
        "• Remote frontend developer\n"
        "• Toshkentda kuryer\n"
        "• Buxgalter junior\n\n"
        "🪙 Har bir qidiruv: *2 coin* (natija topilsa)\n"
        "📞 Bog'lanish ma'lumotlari *bepul* ko'rinadi.\n\n"
        "Iltimos, faqat *ish/kasb* bilan bog'liq yozing."
    ),
    "search_searching": "🔎 *AI yordamida 6 ta platformadan qidirilmoqda...*",
    "search_charged": (
        "🪙 *{cost} coin yechildi.* Topildi: *{count} ta* e'lon.\n"
        "💳 Yangi balans: *{balance}* coin"
    ),
    "search_no_results": (
        "😔 *Hech narsa topilmadi.*\n\n"
        "Coin yechilmadi. Boshqacha so'rov bilan urinib ko'ring:\n"
        "• Boshqa kalit so'z\n"
        "• Yoki kasbingizni boshqacha ifodalang\n\n"
        f"Yordam: {SUPPORT}"
    ),
    "search_daily_limit": (
        "📵 *Kunlik limit tugadi.*\n\n"
        "Free tarifda kuniga *{limit} ta* qidiruv.\n"
        "⭐ *Premium* oling — cheksiz qidiruv va coinsiz!\n\n"
        f"Sotib olish: {SUPPORT}"
    ),
    "search_off_topic": (
        "🤖 *ISH TOP AI* faqat *ish, karyera, kasb* mavzularida yordam beradi.\n\n"
        "❌ Hazil, suhbat, savol-javob — qabul qilinmaydi.\n\n"
        "✅ Misol: «Python dasturchi», «SMM manager», «Toshkentda kuryer»\n\n"
        f"Boshqa savolingiz bo'lsa: {SUPPORT}"
    ),
    "search_insufficient_coins": (
        "🪙 *Coin yetarli emas.*\n\n"
        "Sizda: *{balance}* coin\n"
        "Kerak: *{cost}* coin (har qidiruv uchun)\n\n"
        "💡 Coin ishlash usullari:\n"
        "• 👥 Do'st taklif qilish (+2 coin / +1 coin)\n"
        "• 🎁 Bonus kanallar (+0.5 coin)\n"
        "• ⭐ Premium tarif olish (cheksiz qidiruv)\n\n"
        "«🪙 Coin ishlash» bo'limiga kiring."
    ),
    "search_all_seen": (
        "✅ *Barcha topilgan e'lonlarni ko'rdingiz.*\n\n"
        "Yangi qidiruv qilish uchun «🔍 Ish qidirish» ni bosing."
    ),

    # ---------- Job card ----------
    "btn_job_save": "❤️ Saqlash",
    "btn_job_next": "⏭ Keyingi",
    # Legacy keys (kept so any external reference doesn't break)
    "btn_job_details": "📄 Batafsil",
    "btn_job_contact": "📞 Aloqa",
    "btn_job_unlock": "🔓 Ochish",
    "job_locked_preview": "",
    "job_insufficient_coins": "",
    "job_unlocked": "",
    "job_saved": "❤️ Saqlandi! «❤️ Saqlangan» bo'limidan ko'rishingiz mumkin.",

    # ---------- Profile ----------
    "profile_card": (
        "👤 *Sizning profilingiz*\n\n"
        "🪙 *Coin balansi:* {balance}\n"
        "⭐ *Tarif:* {plan}\n"
        "📅 *Bugungi qidiruvlar:* {searches_today}\n"
        "👥 *Referrallar:* {referrals}\n"
        "❤️ *Saqlangan e'lonlar:* {saved}"
    ),

    # ---------- Plans ----------
    "plans_header": (
        "⭐ *Tariflar*\n\n"
        "Quyidagi tariflardan birini tanlang:"
    ),
    "plan_free": (
        "🆓 *FREE — 0 so'm*\n"
        "  ✅ AI ish qidiruvi\n"
        "  ✅ Bog'lanish bepul\n"
        "  🪙 Har qidiruv = 2 coin\n"
        "  📅 Kuniga 3 ta qidiruv"
    ),
    "plan_premium": (
        "⭐ *PREMIUM — 9 000 so'm/oy*\n"
        "  ✅ Cheksiz qidiruv (coinsiz)\n"
        "  ✅ AI search\n"
        "  ✅ Bog'lanish bepul"
    ),
    "plan_premium_plus": (
        "💎 *PREMIUM+ — 19 990 so'm/oy*\n"
        "  ✅ Cheksiz qidiruv (coinsiz)\n"
        "  ✅ AI search\n"
        "  ✅ Bog'lanish bepul\n"
        "  ✅ AI Career Advisor"
    ),
    "btn_buy_premium": "💳 Premium sotib olish",
    "btn_buy_premium_plus": "💎 Premium+ sotib olish",
    "plan_purchase_message": (
        "💳 *{plan}* tarifini sotib olish uchun admin bilan bog'laning:\n\n"
        f"📩 {SUPPORT}\n\n"
        "Karta orqali to'lov qilingach, tarif darhol faollashtiriladi."
    ),

    # ---------- Earn / Bonus ----------
    "earn_header": (
        "🪙 *Coin ishlash usullari*\n\n"
        "Eslatma: har qidiruv *2 coin* turadi (natija topilsa).\n\n"
        "1. 👥 Do'st taklif qilish — *+2 coin* (1-do'st), keyingi har biri *+1 coin*\n"
        "2. 🎁 Bonus kanallarga qo'shilish — har biri *+0.5 coin*\n"
        "3. ⭐ Premium tarif — coinsiz cheksiz qidiruv"
    ),
    "btn_invite": "👥 Do'st taklif qilish",
    "btn_bonus_channels": "🎁 Bonus kanallar",
    "invite_card": (
        "👥 *Do'stlaringizni taklif qiling*\n\n"
        "🎁 1-do'st uchun: *+2 coin*\n"
        "🎁 Keyingi har biri uchun: *+1 coin*\n\n"
        "📲 *Sizning taklif havolangiz:*\n"
        "`{link}`\n\n"
        "Yoki shu xabarni ulashing 👆\n\n"
        "👥 Hozirgacha taklif qilingan: *{count}* kishi"
    ),
    "bonus_channels_header": (
        "🎁 *Bonus kanallar*\n\n"
        "Har bir kanalga qo'shilsangiz *+0.5 coin* olasiz.\n"
        "Kanalga qo'shilgach «✅ Tekshirish» tugmasini bosing."
    ),
    "bonus_join_btn": "🔗 Qo'shilish",
    "bonus_check_btn": "✅ Tekshirish",
    "bonus_already_claimed": "Bu kanal uchun bonus allaqachon olingan.",
    "bonus_not_subscribed": "❌ Hali kanalga qo'shilmagansiz.",
    "bonus_rewarded": "🎉 +0.5 coin qo'shildi!",
    "bonus_no_channels": (
        "Hozircha bonus kanallar mavjud emas.\n"
        "Qaytib keling — yaqinda qo'shamiz!"
    ),

    # ---------- Help ----------
    "help_text": (
        "ℹ️ *ISH TOP AI — qisqa qo'llanma*\n\n"
        "🔍 *Ish qidirish*\n"
        "AI yordamida 6 ta platformadan vakansiyalar yig'iladi.\n"
        "🪙 Har qidiruv = *2 coin* (natija topilsa).\n"
        "📞 Bog'lanish ma'lumotlari — *bepul*.\n\n"
        "🪙 *Coin ishlash*\n"
        "  • Do'st taklif qilish: *+2 coin* (1-do'st), *+1 coin* (keyingilari)\n"
        "  • Bonus kanal: *+0.5 coin*\n\n"
        "⭐ *Tariflar*\n"
        "  • Free — kuniga 3 qidiruv (har biri 2 coin)\n"
        "  • Premium — cheksiz qidiruv, coinsiz\n"
        "  • Premium+ — cheksiz + AI Career Advisor\n\n"
        "👤 *Profil*\n"
        "Balans, tarif, statistikani ko'ring.\n\n"
        "📞 *Aloqa*\n"
        f"Savol/taklif bo'lsa: {SUPPORT}"
    ),

    # ---------- Advisor ----------
    "advisor_only_premium_plus": (
        "💎 *AI Career Advisor* faqat *Premium+* foydalanuvchilar uchun.\n\n"
        "⭐ *Tariflar* bo'limidan obunani faollashtiring.\n\n"
        f"Yordam: {SUPPORT}"
    ),
    "advisor_prompt": (
        "🧠 *AI Career Advisor*\n\n"
        "Karyera, ko'nikma, roadmap, maosh, intervyu yoki freelancing haqida so'rang.\n\n"
        "Misol:\n"
        "• «Backend developer bo'lish uchun nima o'rganay?»\n"
        "• «Junior frontend maoshi qancha?»\n"
        "• «Texnik intervyuga qanday tayyorgarlik ko'ray?»"
    ),

    # ---------- Admin ----------
    "admin_not_allowed": "⛔ Sizda admin huquqi yo'q.",
    "admin_password_prompt": (
        "🔐 *Admin paroli kiriting:*\n\n"
        "(Parol darhol o'chiriladi)"
    ),
    "admin_password_wrong": "❌ Parol noto'g'ri. Qayta urinib ko'ring yoki `/admin_kirish` ni qayta yuboring.",
    "admin_login_ok": "✅ Admin panelga xush kelibsiz.",
    "admin_session_expired": "⏰ Admin sessiyasi tugadi. Qayta kiring: `/admin_kirish`",
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
