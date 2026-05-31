"""All Uzbek user-facing strings. Bot uses ONLY this dict."""
from __future__ import annotations

from app.config import settings

# Underscore in @cybst_academy must be escaped in legacy Markdown — render as a
# clickable link instead.
SUPPORT_PLAIN = f"@{settings.support_username}"
SUPPORT_URL = f"https://t.me/{settings.support_username}"
SUPPORT = f"[@{settings.support_username.replace('_', chr(92) + '_')}]({SUPPORT_URL})"

T = {
    # ====================================================================
    # GENERAL
    # ====================================================================
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
    "cancel_done": "✅ Bekor qilindi.",

    # ====================================================================
    # /start  &  /menu
    # ====================================================================
    "start_welcome_new": (
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
        "🪙 *Narx:* har qidiruv = *2 coin*\n"
        "(natija topilmasa coin yechilmaydi)\n\n"
        "🎁 *Sovg'a:* sizga *4 coin* BEPUL berildi!\n"
        "(2 ta qidiruv uchun yetadi)\n\n"
        "💡 Ixtiyoriy buyruqlar:\n"
        "  `/menu`   — bosh menyu\n"
        "  `/cancel` — joriy harakatni bekor qilish\n\n"
        f"📩 Yordam kerakmi? {SUPPORT}"
    ),
    "start_welcome_back": (
        "👋 Salom, *{name}*!\n\n"
        "🏠 Bosh menyuga qaytdingiz. Quyidagi bo'limlardan birini tanlang."
    ),
    "main_menu_text": (
        "🏠 *Bosh menyu*\n\n"
        "🔍 *Ish qidirish* — AI yordamida 6 ta saytdan\n"
        "🪙 *Coin ishlash* — referral / bonus / sotib olish\n"
        "⭐ *Tariflar* — Free / Premium / Premium+\n"
        "👤 *Profil* — balans, tarif, saqlangan e'lonlar\n"
        "ℹ️ *Yordam*"
    ),

    # ====================================================================
    # Main menu buttons
    # ====================================================================
    "btn_search": "🔍 Ish qidirish",
    "btn_earn": "🪙 Coin ishlash",
    "btn_plans": "⭐ Tariflar",
    "btn_profile": "👤 Profil",
    "btn_help": "ℹ️ Yordam",
    "btn_advisor": "🧠 AI Career Advisor",

    # ====================================================================
    # Search flow
    # ====================================================================
    "search_who_are_you": "🧠 *Siz kimsiz?*\n\nQuyidagilardan birini tanlang:",
    "btn_role_jobseeker": "👨‍💻 Ish qidiryapman",
    "btn_role_employer": "🏢 Ish beruvchiman",
    "search_query_prompt": (
        "💬 *Qanday ish izlayapsiz?*\n\n"
        "Tabiiy gap bilan ham yozsangiz bo'ladi:\n"
        "• Telegram bot yasab beraman\n"
        "• Web sayt qilib beraman\n"
        "• Toshkentda kuryer bo'lib ishlasam\n"
        "• Uyda ishlaydigan dasturchi\n"
        "• SMM manager kerak\n"
        "• Junior python\n\n"
        "🪙 Har qidiruv: *2 coin* (faqat natija topilsa)\n"
        "📞 Bog'lanish ma'lumotlari *bepul*\n\n"
        "❌ Bekor qilish uchun: `/cancel`"
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
        f"Boshqa savol bo'lsa: {SUPPORT}"
    ),
    "search_insufficient_coins": (
        "🪙 *Coin yetarli emas.*\n\n"
        "Sizda: *{balance}* coin\n"
        "Kerak: *{cost}* coin\n\n"
        "💡 Coin ishlash usullari:\n"
        "• 👥 Do'st taklif qilish\n"
        "• 🎁 Bonus kanallar\n"
        "• 💳 Coin sotib olish\n"
        "• ⭐ Premium tarif\n\n"
        "«🪙 Coin ishlash» bo'limiga kiring."
    ),
    "search_all_seen": (
        "✅ *Barcha topilgan e'lonlarni ko'rdingiz.*\n\n"
        "Yangi qidiruv: «🔍 Ish qidirish» yoki `/menu`"
    ),
    "job_pagination": "📋 *{idx} / {total}*",

    # ====================================================================
    # Job card buttons
    # ====================================================================
    "btn_job_save": "❤️ Saqlash",
    "btn_job_next": "⏭ Keyingi",
    "btn_new_search": "🔄 Yangi qidiruv",
    # Legacy keys
    "btn_job_details": "📄 Batafsil",
    "btn_job_contact": "📞 Aloqa",
    "btn_job_unlock": "🔓 Ochish",
    "job_locked_preview": "",
    "job_insufficient_coins": "",
    "job_unlocked": "",
    "job_saved": "❤️ Saqlandi! «👤 Profil» dan ko'rishingiz mumkin.",

    # ====================================================================
    # Profile
    # ====================================================================
    "profile_card": (
        "👤 *Sizning profilingiz*\n\n"
        "🪙 *Coin balansi:* {balance}\n"
        "⭐ *Tarif:* {plan}\n"
        "📅 *Bugungi qidiruvlar:* {searches_today}\n"
        "👥 *Referrallar:* {referrals}\n"
        "❤️ *Saqlangan e'lonlar:* {saved}"
    ),
    "btn_view_saved": "❤️ Saqlangan e'lonlar ({count})",

    # ====================================================================
    # Saved jobs (NEW)
    # ====================================================================
    "saved_empty": (
        "❤️ *Saqlangan e'lonlar*\n\n"
        "Hali e'lon saqlamagansiz.\n\n"
        "Qidiruv natijalarida «❤️ Saqlash» tugmasini bosing — "
        "shu yerda ko'rishingiz mumkin bo'ladi."
    ),
    "saved_list_header": (
        "❤️ *Saqlangan e'lonlar* — jami: *{total}*\n"
        "📄 Sahifa: *{page}/{pages}*\n\n"
        "Birini tanlang ↓"
    ),
    "saved_deleted": "🗑 O'chirildi.",

    # ====================================================================
    # Plans
    # ====================================================================
    "plans_header": "⭐ *Tariflar*\n\nQuyidagi tariflardan birini tanlang:",
    "plan_free": (
        "🆓 *FREE — 0 so'm*\n"
        "  ✅ AI ish qidiruvi\n"
        "  ✅ Bog'lanish bepul\n"
        "  🪙 Har qidiruv = 2 coin\n"
        "  📅 Kuniga 3 ta qidiruv"
    ),
    "plan_premium": (
        "⭐ *PREMIUM — {price} so'm/oy*\n"
        "  ✅ Cheksiz qidiruv (coinsiz)\n"
        "  ✅ AI search\n"
        "  ✅ Bog'lanish bepul"
    ),
    "plan_premium_plus": (
        "💎 *PREMIUM+ — {price} so'm/oy*\n"
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

    # ====================================================================
    # Earn / Bonus
    # ====================================================================
    "earn_header": (
        "🪙 *Coin ishlash usullari*\n\n"
        "Eslatma: har qidiruv *2 coin* turadi (natija topilsa).\n\n"
        "1️⃣ 👥 *Do'st taklif qilish*\n"
        "   1-do'st: +2 coin · keyingilari: +1 coin\n\n"
        "2️⃣ 🎁 *Bonus kanallarga qo'shilish*\n"
        "   Har kanal: +0.5 coin\n\n"
        "3️⃣ 💳 *Coin sotib olish*\n"
        "   10 / 50 / 100 / 200 coin paketlari\n\n"
        "4️⃣ ⭐ *Premium tarif*\n"
        "   Coinsiz cheksiz qidiruv"
    ),
    "btn_invite": "👥 Do'st taklif qilish",
    "btn_bonus_channels": "🎁 Bonus kanallar",
    "btn_buy_coins": "💳 Coin sotib olish",
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
        "Har kanalga qo'shilsangiz *+0.5 coin* olasiz.\n"
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

    # ====================================================================
    # Coin purchase
    # ====================================================================
    "coins_packages_header": (
        "💳 *Coin sotib olish*\n\n"
        "Quyidagi paketlardan birini tanlang.\n"
        "Tanlagandan so'ng to'lov ko'rsatmasi chiqadi."
    ),
    "purchase_instructions": (
        "✅ *So'rov yaratildi: #{id}*\n\n"
        "🪙 Olish: *{coins} coin*\n"
        "💵 To'lov: *{price} so'm*\n\n"
        "📲 *Qadamlar:*\n"
        "1️⃣ Quyidagi kartaga *{price} so'm* o'tkazing:\n"
        "   `" + settings.payment_card_number + "`\n"
        "   *Karta egasi:* " + settings.payment_card_owner + "\n\n"
        "2️⃣ To'lov chekini (skrinshot) admin'ga yuboring:\n"
        f"   {SUPPORT}\n\n"
        "3️⃣ Sarlavhada so'rov ID'ni yozing: `#{id}`\n\n"
        "⏱ Admin tasdiqlagandan so'ng *{coins} coin* hisobingizga "
        "darhol qo'shiladi va sizga xabar yuboriladi.\n\n"
        "❌ Bekor qilish uchun pastdagi tugmani bosing."
    ),
    "purchase_cancelled": "❌ So'rov #{id} bekor qilindi.",

    # ====================================================================
    # Help
    # ====================================================================
    "help_text": (
        "ℹ️ *ISH TOP AI — qisqa qo'llanma*\n\n"
        "🔍 *Ish qidirish*\n"
        "AI yordamida 6 ta platformadan vakansiyalar yig'iladi.\n"
        "🪙 Har qidiruv: 2 coin (natija topilsa)\n"
        "📞 Bog'lanish: bepul\n\n"
        "🪙 *Coin ishlash*\n"
        "  • Do'st taklif: +2 / +1 coin\n"
        "  • Bonus kanal: +0.5 coin\n"
        "  • Sotib olish: 10/50/100/200 paket\n\n"
        "⭐ *Tariflar*\n"
        "  • Free — 3 qidiruv/kun\n"
        "  • Premium — cheksiz, coinsiz\n"
        "  • Premium+ — + AI Career Advisor\n\n"
        "👤 *Profil* — balans, tarif, saqlangan\n\n"
        "💡 *Buyruqlar:*\n"
        "  `/start`  — boshlash\n"
        "  `/menu`   — bosh menyu\n"
        "  `/cancel` — joriy harakatni bekor qilish\n"
        "  `/help`   — shu yordam\n\n"
        f"📞 *Aloqa:* {SUPPORT}"
    ),

    # ====================================================================
    # Advisor
    # ====================================================================
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
        "• «Texnik intervyuga qanday tayyorgarlik ko'ray?»\n\n"
        "❌ Bekor qilish: `/cancel`"
    ),

    # ====================================================================
    # User notifications (sent by admin actions)
    # ====================================================================
    "user_balance_credited_notify": (
        "🎉 *Sizning hisobingizga {delta} coin qo'shildi!*\n\n"
        "💳 Yangi balans: *{balance}* coin"
    ),
    "user_plan_granted_notify": (
        "🎉 *Sizga {plan} tarifi berildi!*\n\n"
        "⏱ Amal qilish muddati: *{days} kun*\n"
        "Ish izlashda omad! 🎯"
    ),

    # ====================================================================
    # ADMIN — login + dashboard
    # ====================================================================
    "admin_not_allowed": "⛔ Sizda admin huquqi yo'q.",
    "admin_password_prompt": (
        "🔐 *Admin paroli kiriting:*\n\n"
        "(Parol darhol o'chiriladi)\n\n"
        "❌ Bekor qilish: `/cancel`"
    ),
    "admin_password_wrong": "❌ Parol noto'g'ri. Qayta urinib ko'ring yoki `/admin_kirish` ni qayta yuboring.",
    "admin_session_expired": "⏰ Admin sessiyasi tugadi. Qayta kiring: `/admin_kirish`",
    "admin_login_ok": "✅ Admin panelga xush kelibsiz.",
    "admin_logged_out": "👋 Admin panelidan chiqildi. Qayta kirish: `/admin_kirish`",
    "admin_dashboard": (
        "🎛 *ADMIN PANEL*\n\n"
        "👥 *Foydalanuvchilar*\n"
        "  Jami: *{total_users}*\n"
        "  Faol (7 kun): *{active_7d}*\n"
        "  Bugun ro'yxatdan o'tgan: *{today_signups}*\n"
        "  Premium: *{premium_count}*\n\n"
        "🔍 *Qidiruvlar*\n"
        "  Jami: *{searches_total}*\n"
        "  Bugun: *{today_searches}*\n\n"
        "💰 *Daromad*\n"
        "  Bugun: *{today_revenue} so'm*\n"
        "  Jami: *{total_revenue} so'm*\n\n"
        "🪙 *Coin*\n"
        "  Sarflangan: *{coins_spent}*\n\n"
        "🔔 Tasdiqlanmagan to'lovlar: *{pending}*\n\n"
        "👇 Pastdagi tugmalardan birini tanlang"
    ),
    "btn_admin_users": "👥 Userlar",
    "btn_admin_payments": "💳 To'lovlar",
    "btn_admin_stats": "📊 Statistika",
    "btn_admin_broadcast": "📢 Xabar yuborish",
    "btn_admin_bonus": "🎁 Bonus kanallar",
    "btn_admin_logs": "📂 Loglar",
    "btn_admin_logout": "🔓 Chiqish",
    # Legacy keys
    "admin_panel_title": "🎛 *Admin panel*",
    "admin_panel_text": "🎛 *Admin panel*\nTasdiqlanmagan to'lovlar: *{pending}*",
    "btn_admin_blocks": "🚫 Block",
    "btn_admin_plans": "⭐ Tariflar",
    "btn_admin_balance": "🪙 Balans",
    "btn_admin_settings": "⚙️ Sozlamalar",
    "btn_admin_security": "🛡 Security",

    # ====================================================================
    # ADMIN — Users
    # ====================================================================
    "admin_users_help": (
        "👥 *Userlar boshqaruvi*\n\n"
        "Foydalanuvchini qidirish uchun shu chatga *yozing*:\n"
        "  `8392229980`         — ID raqami\n"
        "  `@username`          — username\n"
        "  `username`           — @ siz ham bo'ladi\n"
        "  `/find @user`        — eski uslub\n\n"
        "📋 Karta chiqadi:\n"
        "  • 🪙 Coin qo'shish/ayirish\n"
        "  • ⭐ Tarif berish (Free / Premium / Premium+)\n"
        "  • 🚫 Bloklash / Blokdan chiqarish"
    ),
    "admin_user_not_found": "❌ Foydalanuvchi topilmadi. ID yoki @username to'g'riligini tekshiring.",
    "admin_user_card": (
        "👤 *Foydalanuvchi ma'lumotlari*\n\n"
        "🆔 ID: `{user_id}`\n"
        "👤 Ism: {full_name}\n"
        "📛 Username: {username}\n"
        "⭐ Tarif: *{plan}*\n"
        "🪙 Coin: *{coins}*\n"
        "👥 Referrallar: {referrals}\n"
        "❤️ Saqlangan: {saved}\n"
        "📅 Ro'yxatdan o'tgan: {registered}\n"
        "🔓 Holati: {block_status}"
    ),
    "admin_pick_plan": (
        "⭐ *User `{user_id}` uchun tarif tanlang:*\n\n"
        "• 🆓 Free — bepul, kuniga 3 qidiruv\n"
        "• ⭐ Premium — 30 kunga\n"
        "• 💎 Premium+ — 30 kunga (AI Advisor bilan)"
    ),
    "admin_plan_granted": (
        "✅ *Tarif berildi!*\n\n"
        "🆔 User: `{user_id}`\n"
        "⭐ Tarif: *{plan}*\n"
        "⏱ Muddat: *{days} kun*\n\n"
        "Foydalanuvchiga avtomatik xabar yuborildi."
    ),

    # ====================================================================
    # ADMIN — Balance
    # ====================================================================
    "admin_balance_prompt": (
        "🪙 *User `{user_id}` uchun coin qo'shing/oling*\n\n"
        "Sonni yuboring:\n"
        "  • `10`   — qo'shadi\n"
        "  • `-5`   — oladi\n"
        "  • `2.5`  — kasr ham mumkin\n\n"
        "❌ Bekor qilish: `/cancel`"
    ),
    "admin_balance_bad_amount": "❌ Noto'g'ri son. Misol: `10`, `-5`, `2.5`",
    "admin_balance_done": (
        "✅ *Bajarildi!*\n\n"
        "🆔 User: `{user_id}`\n"
        "🪙 O'zgartirish: *{delta}*\n"
        "💳 Yangi balans: *{balance}*"
    ),

    # ====================================================================
    # ADMIN — Payments
    # ====================================================================
    "admin_payments_empty": (
        "💳 *To'lovlar*\n\n"
        "✅ Hozircha tasdiqlanmagan to'lov so'rovlari yo'q."
    ),
    "admin_payments_header": (
        "💳 *Tasdiqlanishi kutilayotgan to'lovlar: {count} ta*\n\n"
        "Quyida har bir so'rov alohida ko'rsatiladi.\n"
        "✅ Tasdiqlasangiz — coin user hisobiga o'tadi va xabar yuboriladi.\n"
        "❌ Rad etsangiz — user xabardor qilinadi."
    ),
    "admin_payment_not_found": "❌ So'rov topilmadi yoki allaqachon ko'rib chiqilgan.",
    "admin_payment_confirmed": (
        "✅ *To'lov #{id} tasdiqlandi!*\n\n"
        "🆔 User: `{user_id}`\n"
        "🪙 *+{coins} coin* qo'shildi\n"
        "💳 Yangi balans: *{balance}*\n\n"
        "Foydalanuvchiga avtomatik xabar yuborildi."
    ),
    "admin_payment_rejected": (
        "❌ *To'lov #{id} rad etildi.*\n\n"
        "🆔 User: `{user_id}`\n"
        "🪙 So'rov: {coins} coin\n\n"
        "Foydalanuvchiga avtomatik xabar yuborildi."
    ),

    # ====================================================================
    # ADMIN — Statistics (full)
    # ====================================================================
    "admin_stats_full": (
        "📊 *To'liq statistika*\n\n"
        "👥 *Foydalanuvchilar*\n"
        "  Jami: *{total_users}*\n"
        "  Bugun yangi: *{today_signups}*\n"
        "  Faol (1 kun): *{active_1d}*\n"
        "  Faol (7 kun): *{active_7d}*\n"
        "  Faol (30 kun): *{active_30d}*\n"
        "  Premium: *{premium_count}*\n"
        "  Bloklangan: *{blocked}*\n\n"
        "🔍 *Faollik*\n"
        "  Jami qidiruvlar: *{searches}*\n"
        "  AI so'rovlari: *{ai_calls}*\n"
        "  Referrallar: *{refs}*\n\n"
        "💰 *Daromad*\n"
        "  Bugun: *{today_revenue} so'm*\n"
        "  7 kun: *{week_revenue} so'm*\n"
        "  Jami: *{total_revenue} so'm*\n"
        "  Sotuvlar soni: *{purchases_total}*\n\n"
        "🪙 *Coin oqimi*\n"
        "  Sarflangan: *{coins_spent}*\n"
        "  Berilgan: *{coins_credited}*"
    ),

    # ====================================================================
    # ADMIN — Block (NEW reply-button flow)
    # ====================================================================
    "admin_block_prompt": (
        "🚫 *BLOKLASH / BLOKDAN CHIQARISH*\n\n"
        "Foydalanuvchi ID yoki @username ni yozing:\n\n"
        "Misol:\n"
        "  `8392229980`\n"
        "  `@username`\n\n"
        "Agar user *bloklangan* bo'lsa — *blokdan chiqariladi*.\n"
        "Aks holda — *bloklanadi*.\n\n"
        "❌ Bekor qilish: `/cancel`"
    ),
    "admin_block_done": (
        "{flag}\n\n"
        "🆔 User: `{user_id}`\n"
        "📛 Username: {username}"
    ),

    # ====================================================================
    # ADMIN — OBUNA (subscriptions section)
    # ====================================================================
    "admin_subs_header": (
        "💳 *OBUNA — Foydalanuvchi tariflari*\n\n"
        "Bu yerda *coin sotib olish* so'rovlarini tasdiqlash mumkin.\n"
        "Yoki *to'g'ridan-to'g'ri* userga tarif ulash:\n"
        "👇 Pastdagi tugmani bosing"
    ),
    "admin_grant_plan_prompt": (
        "➕ *Userga tarif ulash*\n\n"
        "User ID yoki @username yuboring:\n\n"
        "Misol:\n"
        "  `8392229980`\n"
        "  `@username`\n\n"
        "❌ Bekor qilish: `/cancel`"
    ),
    "admin_grant_plan_pick": (
        "👤 *Topildi:*\n\n"
        "🆔 ID: `{user_id}`\n"
        "👤 Ism: {full_name}\n"
        "📛 Username: {username}\n"
        "⭐ Joriy tarif: *{current_plan}*\n\n"
        "Quyidagi tariflardan birini tanlang 👇"
    ),
    "admin_tarif_usage": (
        "Tezkor buyruq:\n"
        "  `/tarif <user_id> <plan>`\n\n"
        "*plan* qiymatlari: `free` / `premium` / `premium_plus`\n\n"
        "Misol:\n"
        "  `/tarif 8392229980 premium`\n"
        "  `/tarif 8392229980 premium_plus`"
    ),

    # ====================================================================
    # ADMIN — Prices editor (NEW)
    # ====================================================================
    "admin_price_prompt": (
        "💰 *{label}* o'zgartirilmoqda\n\n"
        "Joriy qiymat: *{current}*\n\n"
        "Yangi qiymatni yuboring (faqat raqam):\n"
        "❌ Bekor qilish: `/cancel`"
    ),
    "admin_price_bad_value": "❌ Noto'g'ri qiymat. Faqat musbat son yuboring.",
    "admin_price_done": (
        "✅ *Saqlandi!*\n\n"
        "{label}: *{value}*\n\n"
        "O'zgartirish darhol kuchga kirdi."
    ),

    # ====================================================================
    # ADMIN — Broadcast (UX text refresh)
    # ====================================================================
    "admin_broadcast_prompt": (
        "📢 *XABAR YUBORISH*\n\n"
        "Yubormoqchi bo'lgan matnni yozing.\n"
        "Markdown qo'llab quvvatlanadi (*qalin*, _kursiv_, `kod`).\n\n"
        "❌ Bekor qilish: `/cancel`"
    ),
    "admin_broadcast_confirm": (
        "Tasdiqlash uchun `START` deb yozing.\n"
        "Bekor qilish: `/cancel`"
    ),
    "admin_broadcast_started": "📤 0 / {total}",
    "admin_broadcast_progress": "📤 {i} / {total}  (✅ {sent}  ❌ {failed})",
    "admin_broadcast_done": (
        "✅ *Yuborildi:* {sent}\n"
        "❌ *Xato:* {failed}"
    ),

    # ====================================================================
    # plan names
    # ====================================================================
    "plan_name_free": "Free",
    "plan_name_premium": "Premium",
    "plan_name_premium_plus": "Premium+",
}
