"""
FinPlanner Pro MAX — Mehmonxona + Moliya + Sog'liq + Retseptlar + Reception Bot
"""

import os, json, re, datetime, random
from collections import Counter
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = "8804626503:AAEAGQgsN-SkPCa5Y_rmEVe6GMdZQrgvT-E"
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "data.json")

HOTELS = [
    "🏨 Golden Degrez Hotel",
    "🏨 Buxoro Air Hotel",
    "🏨 Anor Hotel",
    "🏨 Muxsin Hotel",
    "🏨 Temur Hotel",
    "🏨 Al Buxari Hotel",
    "🏨 Al Fayz Hotel",
    "🏨 Joyzar Hotel",
]

EXPENSE_CATS = [
    "💧 Suv", "⚡ Elektr", "🔥 Gaz", "🌐 Internet",
    "🍔 Ovqat", "🚌 Transport", "🏥 Sog'liq",
    "🛍 Xarid", "📚 Ta'lim", "🏠 Uy xarajat",
    "🔧 Ta'mirlash", "🐈 Semxon", "🔑 Ijara haqi", "👩 Apa Marjona", "📦 Boshqa", "🔙 Orqaga"
]

INCOME_CATS = [
    "👷 Ish haqi", "💼 Boshqa", "🔙 Orqaga"
]

XONA_TURLARI = [
    {"nom": "🛏️ SINGL ROOM",  "narx": "300,000 so'm/kecha"},
    {"nom": "🛏️ DABL ROOM",   "narx": "450,000 so'm/kecha"},
    {"nom": "🏨 TRIPLE ROOM", "narx": "800,000 so'm/kecha"},
]

XIZMATLAR = [
    "🍳 Restoran — 07:00–22:00 (nonushta narxga kiradi)",
    "📶 Bepul Wi-Fi — barcha xonalarda",
    "🚗 Aeroport transfer — bepul (band qilishda aytish kerak)",
    "👔 Kir yuvish xizmati — 24 soatda tayyor",
    "💆 Spa & massaj — 10:00–21:00",
    "🅿️ Bepul parking — mehmonxona ichida",
    "🛎️ Room service — 24/7",
]

def reception_faq(topic):
    if topic == "narx":
        lines = "\n".join(f"{x['nom']} — {x['narx']}" for x in XONA_TURLARI)
        return (
            f"💰 *Xona narxlarimiz:*\n\n{lines}\n\n"
            f"✅ Barcha xonalarda nonushta narxga kiradi.\n"
            f"📞 Band qilish: +998 99 583 18 28"
        )
    elif topic == "band":
        return (
            "🛏️ *Xona band qilish:*\n\n"
            "Quyidagi ma'lumotlarni yuboring:\n"
            "📅 Kelish sanasi\n📅 Ketish sanasi\n"
            "👥 Mehmonlar soni\n🛏️ Xona turi\n\n"
            "📞 Tel: +998 99 583 18 28\n\n"
            "⚠️ *MUHIM:*\nXonaga kirish *PASPORT* asosida amalga oshiriladi.\n"
            "👥 2 kishilik xonada — ikkala mehmonda ham pasport bo'lishi shart.\n"
            "🪪 Pasport, uning rasmi, *MyGov* ilovasi, ID karta yoki haydovchilik guvohnomasi bilan ham qabul qilinadi."
        )
    elif topic == "checkin":
        return (
            "🕐 *Check-in / Check-out:*\n\n"
            "✅ Check-in: 14:00 dan\n"
            "🚪 Check-out: 12:00 gacha\n\n"
            "💡 Erta kelsangiz bagajingizni saqlaymiz.\n"
            "📞 Tel: +998 99 583 18 28"
        )
    elif topic == "xizmat":
        lines = "\n".join(f"  • {x}" for x in XIZMATLAR)
        return f"✨ *Xizmatlarimiz:*\n\n{lines}"
    elif topic == "pasport":
        return (
            "🪪 *Pasport talabi — MUHIM:*\n\n"
            "Xona *PASPORT* asosida beriladi.\n\n"
            "👥 2 kishilik xonada — ikkala mehmonda ham pasport bo'lishi shart.\n\n"
            "✅ Qabul qilinadi:\n  • Asl pasport\n  • Pasport rasmi (surati)\n  • *MyGov* ilovasidan ko'rsatilgan pasport\n  • ID karta\n  • Haydovchilik guvohnomasi"
        )
    elif topic == "manzil":
        return (
            "📍 *Manzilimiz:*\n\nBuxoro sh.\n\n"
            "📞 Tel: +998 99 583 18 28"
        )
    elif topic == "ovqat":
        return (
            "🍽️ *Ovqatlanish:*\n\n"
            "🌅 Nonushta: 07:00–10:00 (narxga kiradi)\n"
            "☀️ Tushlik: 12:00–15:00\n"
            "🌙 Kechki: 18:00–22:00\n\n"
            "🛎️ Room service 24/7"
        )
    elif topic == "kontakt":
        return (
            "📞 *Aloqa:*\n\n"
            "📱 Tel: +998 99 583 18 28\n"
            "🕐 Reception: 24/7"
        )
    return ""

MEALS = {
    "nonushta": [
        {"nom": "Tuxum va sabzavotli omlet","kaloria": 280,"oqsil": "22g","yog": "18g","uglevod": "4g",
         "ingredientlar": ["3 ta tuxum","1/2 qizil qalampir","1/2 piyoz","1 pomidor","1 tsp zaytun moyi","Tuz, qora murch"],
         "tayyorlash": "1️⃣ Tuxumlarni chayqab, tuz soling.\n2️⃣ Zaytun moyida sabzavotlarni qovuring.\n3️⃣ Tuxumni quying, 3-4 daqiqa pishiring.",
         "foyda": "🔥 To'yimli | ⚡ Energiya beradi"},
        {"nom": "Ovsyanka + meva","kaloria": 320,"oqsil": "12g","yog": "6g","uglevod": "52g",
         "ingredientlar": ["80g ovsyanka","200ml sut","1 banan","1 tsp asal","Yong'oq"],
         "tayyorlash": "1️⃣ Ovsyankani qaynayotgan suvga soling.\n2️⃣ 5 daqiqa pishiring.\n3️⃣ Banan va asal soling.",
         "foyda": "🌾 Uzoq to'ydiradi | 💓 Yurak uchun foydali"},
    ],
    "tushlik": [
        {"nom": "Tovuq ko'kragi + sabzavot","kaloria": 380,"oqsil": "42g","yog": "12g","uglevod": "18g",
         "ingredientlar": ["200g tovuq","1 brokoli","1 zucchini","2 tsp zaytun moyi","Tuz, zira"],
         "tayyorlash": "1️⃣ Tovuqni marinada qiling.\n2️⃣ 180°C da 20 daqiqa pishiring.\n3️⃣ Sabzavotlarni qovuring.",
         "foyda": "💪 Ko'p oqsil | 🔥 Kam kaloriya"},
        {"nom": "Baliq + guruch","kaloria": 450,"oqsil": "38g","yog": "16g","uglevod": "35g",
         "ingredientlar": ["180g losos","100g guruch","1 bodring","2 pomidor","Limon"],
         "tayyorlash": "1️⃣ Guruchni qaynatib pishiring.\n2️⃣ Baliqni bug'da pishiring.\n3️⃣ Salat tayyorlang.",
         "foyda": "🐟 Omega-3 | 🧠 Miya uchun foydali"},
    ],
    "kechki": [
        {"nom": "Bug'da baliq + sabzavot","kaloria": 290,"oqsil": "34g","yog": "10g","uglevod": "12g",
         "ingredientlar": ["200g oq baliq","1 brokoli","1 sabzi","Limon, tuz"],
         "tayyorlash": "1️⃣ Baliqni marinada qiling.\n2️⃣ Bug'da 15-18 daqiqa pishiring.",
         "foyda": "🌙 Kechga engil | 💪 Oqsilga boy"},
        {"nom": "Tovuq shorva","kaloria": 210,"oqsil": "30g","yog": "5g","uglevod": "14g",
         "ingredientlar": ["200g tovuq","1 sabzi","1 piyoz","1/2 karam","Ukrop, limon"],
         "tayyorlash": "1️⃣ Tovuqni 20 daqiqa qaynatib ko'pigini oling.\n2️⃣ Sabzavotlarni qo'shing.\n3️⃣ 15 daqiqa qaynatib ukrop soling.",
         "foyda": "🍵 Eng engil kechki ovqat"},
    ],
    "snack": [
        {"nom": "Yong'oq aralashmasi","kaloria": 180,"oqsil": "5g","yog": "15g","uglevod": "8g",
         "ingredientlar": ["10 ta bodom","10 ta yong'oq","5 ta keshyu"],
         "tayyorlash": "✅ Tayyor!","foyda": "🔥 Metabolizmni tezlashtiradi"},
        {"nom": "Qatiq + bodring","kaloria": 120,"oqsil": "8g","yog": "3g","uglevod": "14g",
         "ingredientlar": ["200g qatiq","1 bodring","Tuz"],
         "tayyorlash": "✅ Bodringni to'g'rang, qatiq bilan yeng.","foyda": "💧 Suvsizlikni qondiradi"},
    ]
}

MASHQLAR = [
    {"nom": "🔥 Qorin uchun 5 ta mashq","vaqt": "20 daqiqa",
     "mashqlar": [("Plank","3 × 30-45 soniya","Qorin mushaklarini mustahkamlaydi"),
                  ("Bicycle crunch","3 × 20 marta","Qorin yog'ini eng tez yoqadi"),
                  ("Mountain climber","3 × 30 soniya","Yurak urishi va yog' yoqish"),
                  ("Leg raises","3 × 15 marta","Quyi qorin uchun"),
                  ("Russian twist","3 × 20 marta","Yon qorin va bel")]},
    {"nom": "🚶 Ofis uchun faollik","vaqt": "Kun davomida",
     "mashqlar": [("Har 1 soatda 5 daqiqa yurish","Kun bo'yi","Metabolizmni faol saqlaydi"),
                  ("Lift o'rniga zinapoya","Har safar","Yurak va oyoq mushaklari"),
                  ("Tushlikda 15 daqiqa yurish","Har kuni","Kaloriya yoqish"),
                  ("Suv ichish (2-2.5L)","Kun davomida","Yog' almashinuvini yaxshilaydi")]},
]

QOIDALAR = [
    "🕗 Kechki 20:00 dan keyin ovqat emang",
    "💧 Kuniga 2-2.5 litr suv iching",
    "🍽 3 asosiy ovqat + 1-2 snack",
    "🚫 Qand va oq un mahsulotlarini kamaytiring",
    "🥗 Har ovqatda sabzavot bo'lsin",
    "🏃 Har kuni kamida 8000 qadam yuring",
    "😴 7-8 soat uxlang",
    "⏰ Ovqatlar orasida 3-4 soat bo'lsin",
]

(MENU, HOTEL_SELECT, HOTEL_AMOUNT,
 INCOME_CAT, INCOME_AMOUNT, EXPENSE_CAT, EXPENSE_AMOUNT,
 TASK_TEXT, TASK_TIME, BUDGET_SET, WEIGHT_LOG) = range(11)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, uid):
    uid = str(uid)
    if uid not in data:
        data[uid] = {"balance": 0, "income": 0, "expense": 0, "transactions": [],
                     "tasks": [], "budget_limit": 0, "hotel_income": {},
                     "monthly_hotels": {}, "weight_log": []}
    for k in ["hotel_income","tasks","transactions","monthly_hotels","weight_log"]:
        if k not in data[uid]:
            data[uid][k] = {} if k in ["hotel_income","monthly_hotels"] else []
    return data[uid]

MAIN_KB = ReplyKeyboardMarkup([
    ["🏨 Mehmonxona daromad", "💸 Xarajat"],
    ["➕ Boshqa daromad",     "💰 Balans"],
    ["📊 Hisobot",            "📈 Grafik"],
    ["🥗 Ovqat & Sog'liq",   "📅 Kun tartibi"],
    ["✅ Vazifalar",          "⚙️ Sozlamalar"],
    ["🛎️ Reception Bot",     "📞 Aloqa"],
], resize_keyboard=True)

def hotel_kb():
    rows = [HOTELS[i:i+2] for i in range(0, len(HOTELS), 2)]
    rows.append(["🔙 Orqaga"])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def expense_kb():
    rows = [EXPENSE_CATS[i:i+2] for i in range(0, len(EXPENSE_CATS), 2)]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def income_kb():
    rows = [INCOME_CATS[i:i+2] for i in range(0, len(INCOME_CATS), 2)]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    get_user(data, update.effective_user.id)
    save_data(data)
    await update.message.reply_text(
        f"Assalomu alaykum, *{update.effective_user.first_name}*! 👋\n\n"
        "🏨 *FinPlanner Pro MAX*\n"
        "━━━━━━━━━━━━━━━\n\n"
        "• 🏨 Mehmonxona daromadlari\n"
        "• 📈 Grafik hisobotlar\n"
        "• 🥗 Sog'liq va retseptlar\n"
        "• 🛎️ Reception Bot\n\n"
        "Menyudan tanlang 👇",
        parse_mode="Markdown", reply_markup=MAIN_KB)
    return MENU

async def reception_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Xona narxlari",        callback_data="rec_narx")],
        [InlineKeyboardButton("🛏️ Xona band qilish",     callback_data="rec_band")],
        [InlineKeyboardButton("🕐 Check-in / Check-out", callback_data="rec_checkin")],
        [InlineKeyboardButton("✨ Xizmatlarimiz",         callback_data="rec_xizmat")],
        [InlineKeyboardButton("🪪 Pasport talabi",        callback_data="rec_pasport")],
        [InlineKeyboardButton("🍽️ Restoran & Ovqat",     callback_data="rec_ovqat")],
        [InlineKeyboardButton("📍 Manzil",                callback_data="rec_manzil")],
        [InlineKeyboardButton("📞 Kontakt",               callback_data="rec_kontakt")],
    ])
    await update.message.reply_text(
        "🛎️ *Mehmonxona Reception Bot*\n"
        "━━━━━━━━━━━━━━━\n\n"
        "Assalomu alaykum! Sizga qanday yordam bera olaman?\n\n"
        "⚠️ Xonaga kirish uchun *PASPORT* talab qilinadi!",
        parse_mode="Markdown", reply_markup=kb)
    return MENU

async def reception_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    topic = q.data.replace("rec_", "")
    if topic == "back":
        return await reception_back_callback(update, ctx)
    msg = reception_faq(topic)
    if not msg:
        await q.message.reply_text("❌ Ma'lumot topilmadi.")
        return MENU
    back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="rec_back")]])
    await q.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_kb)
    return MENU

async def reception_back_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Xona narxlari",        callback_data="rec_narx")],
        [InlineKeyboardButton("🛏️ Xona band qilish",     callback_data="rec_band")],
        [InlineKeyboardButton("🕐 Check-in / Check-out", callback_data="rec_checkin")],
        [InlineKeyboardButton("✨ Xizmatlarimiz",         callback_data="rec_xizmat")],
        [InlineKeyboardButton("🪪 Pasport talabi",        callback_data="rec_pasport")],
        [InlineKeyboardButton("🍽️ Restoran & Ovqat",     callback_data="rec_ovqat")],
        [InlineKeyboardButton("📍 Manzil",                callback_data="rec_manzil")],
        [InlineKeyboardButton("📞 Kontakt",               callback_data="rec_kontakt")],
    ])
    await q.message.reply_text("🛎️ *Reception menyusi:*", parse_mode="Markdown", reply_markup=kb)
    return MENU

async def contact_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(reception_faq("kontakt"), parse_mode="Markdown", reply_markup=MAIN_KB)
    return MENU

GURUH_KEYWORDS = {
    ("narx","qancha","price","necha"): "narx",
    ("band","bron","rezerv","book"): "band",
    ("check","kirish vaqt","soat"): "checkin",
    ("xizmat","wifi","parking","spa"): "xizmat",
    ("pasport","hujjat","dokument"): "pasport",
    ("manzil","qayerda","adres"): "manzil",
    ("telefon","kontakt","aloqa"): "kontakt",
}

FAQ_LIST = [
    # 1. Bandlash va rezervatsiya
    ("Xonani qanday bron qilsam bo'ladi?", "Telegram bot, Instagram DM yoki telefon orqali (+998 99 583 18 28) bron qiling; sana, xona turi va mehmonlar sonini ayting, biz qisqa vaqt ichida tasdiqlaymiz."),
    ("Bron qilish uchun oldindan to'lov kerakmi?", "Ha, odatda umumiy summaning 20-30% miqdorida oldindan to'lov so'raladi, qolgani kelganingizda to'lanadi."),
    ("Onlayn bron qilish imkoniyati bormi?", "Ha, Telegram botimiz orqali xonalar katalogidan tanlab, to'g'ridan-to'g'ri bron qilishingiz mumkin."),
    ("Bir necha xonani bitta bron qilib bo'ladimi?", "Ha, guruh yoki oilaviy safar uchun bir nechta xonani bitta bron ostida rasmiylashtiramiz, guruh chegirmasi haqida so'rang."),
    ("Bron qilinganini qanday tasdiqlayman?", "Bron qilingandan so'ng botdan yoki administratordan yozma tasdiqnoma (booking confirmation) olasiz."),
    ("Bron qilishda qaysi ma'lumotlarni taqdim etishim kerak?", "Ism-familiya, telefon raqami, kelish-ketish sanalari, mehmonlar soni va xona turi."),
    ("Oxirgi daqiqada (last-minute) bron qilsa bo'ladimi?", "Bo'sh xona mavjud bo'lsa, hatto kelish kunining o'zida ham bron qilish mumkin, botdan bo'sh joylarni tekshiring."),
    ("Bayram va sayyohlik mavsumida xona topish qiyinmi?", "Yuqori mavsumda (bahor-kuz) xonalar tez to'lib qoladi, shuning uchun kamida 1-2 hafta oldin bron qilishni tavsiya qilamiz."),
    ("Bron qilingan sanani o'zgartirsam bo'ladimi?", "Ha, kelish sanasidan kamida 24 soat oldin xabar bersangiz, bepul o'zgartirib beramiz."),
    ("Bron qilish uchun qaysi kanal orqali murojaat qilsam bo'ladi?", "@bezzakshotelbuxoro yoki @hotelbuxhara Telegram kanallarimiz, shuningdek Instagram sahifamiz orqali murojaat qiling."),
    # 2. Xonalar va ularning sharoiti
    ("Qanday xona turlari mavjud?", "Standart, Komfort (Deluxe) va Lyuks (Suite) xonalar, bir kishilik va ikki kishilik variantlarda mavjud."),
    ("Xonalarda konditsioner bormi?", "Ha, barcha xonalarda konditsioner va isitish tizimi o'rnatilgan."),
    ("Xonada shaxsiy hammom bormi?", "Ha, har bir xonada issiq suv bilan ta'minlangan shaxsiy hammom va dush mavjud."),
    ("Xonalarda televizor va Wi-Fi bormi?", "Ha, barcha xonalarda televizor va bepul Wi-Fi mavjud."),
    ("Xona qancha kvadrat metr?", "Standart xonalar taxminan 16-18 m², Lyuks xonalar 25-30 m² atrofida."),
    ("Xonadan hovli yoki ko'cha ko'rinishi tanlash mumkinmi?", "Ha, bron qilishda ko'rinish (hovli/ko'cha) bo'yicha talabingizni bildirsangiz, imkon darajasida hisobga olamiz."),
    ("Xonalarda minibar yoki muzlatgich bormi?", "Lyuks xonalarda minibar mavjud, standart xonalarda so'rov asosida kichik muzlatgich qo'yiladi."),
    ("Xonalar necha kishilik?", "1, 2 yoki 3 kishilik xonalar mavjud, oilaviy xonalarda qo'shimcha yotoq o'rnatish mumkin."),
    ("Xonada seyf (saqlash qutisi) bormi?", "Lyuks xonalarda seyf mavjud, boshqa xonalarda qimmatbaho buyumlaringizni administratorga saqlashga topshirishingiz mumkin."),
    ("Xonalar necha marta tozalanadi?", "Xonalar har kuni tozalanadi, choyshab va sochiqlar 2 kunda bir marta almashtiriladi (talab bo'yicha tezroq ham mumkin)."),
    # 3. Narxlar va to'lov usullari
    ("Bir kechalik narx qancha?", "Narx xona turiga va mavsumga qarab farq qiladi; aniq narxni @hotelbuxhara narxlar kanalidan yoki botdan bilib olishingiz mumkin."),
    ("Narxga nonushta kiradimi?", "Ko'pchilik tariflarda ha, bron qilishda aniq shartni tekshirib oling."),
    ("To'lovni qanday amalga oshirsam bo'ladi?", "Naqd pul, plastik karta (UzCard/Humo) yoki bank o'tkazmasi orqali to'lash mumkin."),
    ("Chet el valyutasida to'lash mumkinmi?", "Ha, dollar yoki so'mda to'lash mumkin, kurs kunlik markaziy bank kursi bo'yicha hisoblanadi."),
    ("Uzoq muddat yashasam chegirma bormi?", "Ha, 7 kundan ortiq turadigan mehmonlarga individual chegirma taqdim etiladi, administrator bilan bog'laning."),
    ("Guruh yoki turfirmalar uchun maxsus narx bormi?", "Ha, guruh bandlovlari va turfirmalar bilan hamkorlik uchun maxsus shartnoma narxlari mavjud."),
    ("Bolalar uchun qo'shimcha to'lov olinadimi?", "6 yoshgacha bo'lgan bolalar bepul, 6-12 yosh oralig'ida chegirmali qo'shimcha to'lov olinadi."),
    ("Turistik soliq yoki qo'shimcha yig'im bormi?", "Narxga barcha soliqlar kiritilgan, qo'shimcha yashirin to'lov yo'q."),
    ("To'lov kvitansiyasi (chek) berasizlarmi?", "Ha, har bir to'lov uchun rasmiy chek yoki hisob-faktura beramiz."),
    ("Karta orqali oldindan onlayn to'lov qilsa bo'ladimi?", "Ha, Telegram bot orqali onlayn to'lov havolasi yuboriladi, karta orqali xavfsiz to'lashingiz mumkin."),
    # 4. Bekor qilish, o'zgartirish va pul qaytarish
    ("Bronni bekor qilsam pulim qaytariladimi?", "Kelish sanasidan 48 soat oldin bekor qilsangiz, oldindan to'lovning to'liq summasi qaytariladi."),
    ("Kech bekor qilsam nima bo'ladi?", "24 soatdan kam vaqt qolganda bekor qilinsa, oldindan to'lovning bir qismi ushlab qolinishi mumkin."),
    ("Kelmay qolsam (no-show) pul qaytariladimi?", "Yo'q, oldindan xabarsiz kelmay qolingan holatda oldindan to'lov qaytarilmaydi."),
    ("Bron sanasini bepul o'zgartirish mumkinmi?", "Ha, kelishdan kamida 24 soat oldin murojaat qilsangiz, sanani bepul ko'chirib beramiz."),
    ("Xona turini boshqasiga almashtirsam bo'ladimi?", "Bo'sh joy mavjud bo'lsa, kelishdan oldin yoki hatto kelgan kuningizda ham xona turini o'zgartirish mumkin."),
    ("Pul qaytarish necha kun ichida amalga oshadi?", "Bekor qilingandan so'ng 3-5 ish kuni ichida to'lov usulingizga qarab pul qaytariladi."),
    ("Favqulodda holatlar (kasallik, parvoz bekor bo'lishi) uchun istisno bormi?", "Ha, hujjat bilan tasdiqlangan favqulodda holatlarda individual tarzda ko'rib chiqamiz."),
    ("Bron shartlarini qayerdan bilib olsam bo'ladi?", "Bron tasdiqlash xabarida bekor qilish va o'zgartirish shartlari aniq ko'rsatiladi."),
    # 5. Kelish (check-in) va ketish (check-out)
    ("Check-in va check-out vaqti nechada?", "Check-in soat 14:00 dan, check-out soat 12:00 gacha."),
    ("Erta check-in yoki kech check-out qilsa bo'ladimi?", "Bo'sh xona mavjud bo'lsa, bepul yoki kichik qo'shimcha to'lov evaziga imkoniyat yaratamiz, oldindan so'rang."),
    ("Kechqurun kech kelsam (masalan tunda) muammo bo'lmaydimi?", "Yo'q, resepshn kunning istalgan vaqtida sizni kutib oladi, faqat kelish vaqtingizni oldindan xabar qiling."),
    ("Check-in uchun qanday hujjat kerak?", "Pasport yoki shaxsni tasdiqlovchi hujjat asl nusxasi kerak bo'ladi (chet ellik mehmonlar uchun ham pasport yetarli)."),
    ("Yuklarimni check-out dan keyin saqlab turasizlarmi?", "Ha, ketish kuni parvozgacha vaqtingiz bo'lsa, yuklaringizni bepul saqlab turamiz."),
    ("Bir nechta mehmon bitta xonaga qo'shilib check-in qilishi mumkinmi?", "Ha, barcha mehmonlarning ma'lumotlari ro'yxatga olinishi sharti bilan mumkin."),
    ("Aeroportdan/vokzaldan to'g'ridan-to'g'ri kelib check-in qilsam bo'ladimi?", "Ha, agar xona tayyor bo'lsa darhol joylashtiramiz, aks holda kutish zonasida kutib turishingiz mumkin."),
    ("Check-out paytida xona holatini tekshirasizlarmi?", "Ha, xodimlarimiz xonani tezda ko'zdan kechiradi, bu odatda bir necha daqiqa vaqt oladi."),
    # 6. Manzil, transport va yetib borish
    ("Mehmonxona Buxoroning qayerida joylashgan?", "Buxoro shahar markaziga yaqin joylashgan, tarixiy diqqatga sazovor joylargacha piyoda yoki qisqa yo'l bilan yetish mumkin (aniq manzil bron tasdiqnomasida ko'rsatiladi)."),
    ("Aeroportdan mehmonxonagacha qancha masofa?", "Buxoro xalqaro aeroportidan taxminan 10-15 daqiqalik yo'l (mashinada)."),
    ("Temir yo'l vokzalidan qanday yetib kelsam bo'ladi?", "Taksi bilan 15-20 daqiqada yetib kelasiz, so'rov bo'lsa transfer tashkil qilib beramiz."),
    ("Aeroport yoki vokzaldan transfer xizmati bormi?", "Ha, oldindan buyurtma bergan mehmonlar uchun pullik transfer xizmati mavjud."),
    ("Mehmonxona yaqinida bepul avtoturargoh bormi?", "Ha, mehmonlar uchun bepul avtoturargoh joyi mavjud."),
    ("Shahar markaziga (Lyabi-Hovuz, Ark qal'asi) yetib borish qulaymi?", "Ha, ko'pchilik diqqatga sazovor joylar piyoda 10-20 daqiqa masofada joylashgan."),
    ("Taksi chaqirish uchun yordam berasizlarmi?", "Ha, resepshn xodimlari ishonchli taksi xizmatini chaqirib beradi yoki Yandex Go orqali buyurtma berishga yordamlashadi."),
    ("Boshqa shaharlardan (Toshkent, Samarqand) qanday yetib kelsam bo'ladi?", "Poyezd (Afrosiyob/Sharq), samolyot yoki avtobus orqali Buxoroga yetib, yuqoridagi transfer variantlaridan foydalanishingiz mumkin."),
    # 7. Nonushta va ovqatlanish
    ("Nonushta soat nechada beriladi?", "Nonushta har kuni soat 07:00 dan 10:00 gacha xizmat qiladi."),
    ("Nonushta narxga kiradimi?", "Ko'pchilik tariflarda ha, bron qilishda aniq shartni tekshirib oling."),
    ("Milliy taomlar bilan tanishtirasizlarmi?", "Ha, nonushtada mahalliy Buxoro taomlari (non, choy, murabbo, tuxum taomlari) taqdim etiladi."),
    ("Tushlik va kechki ovqat xizmati bormi?", "Ba'zi filiallarda restoran mavjud, bo'lmasa yaqin atrofdagi eng yaxshi restoranlarni tavsiya qilamiz."),
    ("Vegetarian yoki maxsus parhez taomlar mavjudmi?", "Ha, oldindan xabar bersangiz, vegetarian yoki boshqa parhez talablariga mos taom tayyorlab beramiz."),
    ("Xonaga ovqat yetkazib berish (room service) xizmati bormi?", "Ha, cheklangan menyu asosida xonaga ovqat yetkazib berish xizmati mavjud."),
    ("Yaqin atrofda choyxona yoki kafega yaqinmi?", "Ha, mehmonxona atrofida bir nechta mahalliy choyxona va kafelar mavjud."),
    ("Ichimlik suvi bepulmi?", "Ha, xonada har kuni bepul ichimlik suvi taqdim etiladi."),
    # 8. Qulayliklar va qo'shimcha xizmatlar
    ("Bepul Wi-Fi butun hududda ishlaydimi?", "Ha, mehmonxonaning barcha hududida (xona, resepshn, hovli) bepul Wi-Fi mavjud."),
    ("Kir yuvish xizmati bormi?", "Ha, pullik kir yuvish va dazmollash xizmati mavjud, ertasi kuni tayyor bo'ladi."),
    ("Sayyohlik gidligi yoki ekskursiya tashkil qilib berasizlarmi?", "Ha, Buxoro bo'ylab shaharni ko'rish ekskursiyalarini tashkil qilib beramiz yoki ishonchli gidlar bilan bog'laymiz."),
    ("24 soatlik resepshn ishlaydimi?", "Ha, resepshn xizmati kecha-kunduz ishlaydi."),
    ("Konferensiya yoki tadbir uchun zal bormi?", "So'rov asosida kichik uchrashuvlar yoki oilaviy tadbirlar uchun joy tashkil qilib beramiz."),
    ("Terassa yoki hovlida dam olish joyi bormi?", "Ha, an'anaviy Buxoro uslubidagi hovlida o'tirish va dam olish zonasi mavjud."),
    ("Valyuta almashtirish xizmati bormi?", "Resepshn orqali yaqin atrofdagi ishonchli almashtirish shoxobchalarini tavsiya qilamiz."),
    ("Sim-karta yoki mahalliy aloqa bo'yicha yordam berasizlarmi?", "Ha, mahalliy sim-karta olishda yordam beramiz va tavsiyalar taqdim etamiz."),
    ("Chamodon/yuk ko'targich (concierge) xizmati bormi?", "Ha, xodimlarimiz yuklaringizni xonagacha olib borishda yordam beradi."),
    ("Xonani bezash (romantik kechqurun, tug'ilgan kun) xizmati bormi?", "Ha, oldindan buyurtma bergan mehmonlar uchun xona bezash xizmatini tashkil qilamiz."),
    # 9. Mehmonxona ichki qoidalari
    ("Xonada chekish mumkinmi?", "Yo'q, barcha yopiq hududlarda chekish taqiqlangan, chekish uchun maxsus tashqi zona ajratilgan."),
    ("Mehmon kutib olsam bo'ladimi (tashqi mehmon)?", "Ha, lekin tashqi mehmonlar kechqurun soat 22:00 gacha resepshnda ro'yxatdan o'tishi kerak."),
    ("Tinchlik soatlari (quiet hours) bormi?", "Ha, soat 23:00 dan 07:00 gacha boshqa mehmonlarga xalaqit bermaslik so'raladi."),
    ("Alkogol ichish mumkinmi?", "Umumiy hududlarda madaniy tarzda iste'mol qilish mumkin, ammo haddan tashqari shovqin va tartibsizlikka yo'l qo'yilmaydi."),
    ("Xonada kir yuvish mashinasidan foydalansam bo'ladimi?", "Xonalarda shaxsiy kir yuvish mashinasi yo'q, mehmonxonaning kir yuvish xizmatidan foydalaning."),
    ("Xona kalitini yo'qotib qo'ysam nima bo'ladi?", "Kalit almashtirish uchun belgilangan nominal to'lov olinadi."),
    ("Mehmonxonada mulkka yetkazilgan zarar uchun javobgarlik bormi?", "Ha, mehmon o'z beparvoligi tufayli yetkazgan zarar uchun javobgar hisoblanadi, zarar bahosi joyida kelishiladi."),
    ("Fotosurat yoki video suratga olish mumkinmi (ijtimoiy tarmoq uchun)?", "Ha, shaxsiy foydalanish uchun mumkin, faqat boshqa mehmonlarning roziligisiz ularni suratga olmaslikni so'raymiz."),
    # 10. Bolalar, uy hayvonlari va maxsus ehtiyojlar
    ("Bolalar bilan kelsam qulayliklar bormi?", "Ha, bolalar krovati (childcot) va qo'shimcha yostiq-ko'rpa so'rov asosida taqdim etiladi."),
    ("Uy hayvonlari bilan turish mumkinmi?", "Ko'pchilik xonalarda uy hayvonlari qabul qilinmaydi, oldindan alohida so'rov qilsangiz ko'rib chiqamiz."),
    ("Nogironligi bo'lgan mehmonlar uchun sharoit bormi?", "Kirish qismida pandus va birinchi qavatda qulay xonalar mavjud, oldindan xabar bering, moslashtirib beramiz."),
    ("Homilador ayollar uchun maxsus sharoit bormi?", "Ha, tinch va qulay xona tanlab beramiz, zaruratda tibbiy yordam chaqirishda ko'maklashamiz."),
    ("Katta yoshdagi (keksa) mehmonlar uchun qulayliklar bormi?", "Ha, birinchi qavat xonalari va liftga yaqin joylarni ustuvor ravishda taklif qilamiz."),
    ("Bolalar uchun nonushta menyusi alohida bormi?", "Ha, so'rov bo'yicha bolalarga moslashtirilgan yengil taomlar tayyorlab beramiz."),
    # 11. Xavfsizlik, Wi-Fi va texnik masalalar
    ("Mehmonxonada video kuzatuv (CCTV) bormi?", "Ha, umumiy hududlarda (kirish, koridor, hovli) video kuzatuv tizimi o'rnatilgan."),
    ("Yong'in xavfsizligi ta'minlanganmi?", "Ha, yong'in signalizatsiyasi va o't o'chirish uskunalari barcha qavatlarda mavjud."),
    ("Qimmatbaho buyumlarimni qayerga saqlasam bo'ladi?", "Resepshnda seyf xizmatidan foydalanishingiz yoki xonadagi seyfdan foydalanishingiz mumkin."),
    ("Wi-Fi ishlamasa nima qilishim kerak?", "Resepshnga murojaat qiling, texnik xodim tezda muammoni hal qiladi yoki routerni qayta ishga tushiradi."),
    ("Elektr uzilib qolsa nima bo'ladi?", "Mehmonxonada zaxira generator mavjud, muhim tizimlar (yoritish, lift) uzilishsiz ishlashda davom etadi."),
    ("Tungi vaqtda xavfsizlik xodimi bormi?", "Ha, kechqurun va tunda navbatchi xodim va qo'riqlash mavjud."),
    # 12. Buxoro shahri va sayyohlik ma'lumotlari
    ("Buxoroda qaysi diqqatga sazovor joylarni ko'rish tavsiya etiladi?", "Ark qal'asi, Poi Kalon majmuasi, Lyabi-Hovuz, Chor-Minor va Bolo-Hovuz masjidini albatta ko'ring."),
    ("Bu joylargacha mehmonxonadan qancha vaqt ketadi?", "Ko'pchiligi piyoda 10-25 daqiqa, uzoqroqlari taksida 5-10 daqiqa masofada."),
    ("Buxoroda eng yaxshi tashrif buyurish mavsumi qachon?", "Bahor (aprel-may) va kuz (sentyabr-oktyabr) oylari harorat qulay bo'lgani uchun eng maqbul mavsum hisoblanadi."),
    ("Milliy hunarmandchilik bozorlarini qayerdan topsam bo'ladi?", "Toqi Zargaron va Toqi Sarrofon savdo gumbazlarida mahalliy hunarmandlar mahsulotlarini topasiz."),
    ("Buxoroda kunlik qancha vaqt sarflash yetarli?", "To'liq tanishish uchun 2-3 kun tavsiya etiladi, shoshilinch dastur uchun 1 kun ham yetarli."),
    ("Gid xizmatidan qanday foydalansam bo'ladi?", "Resepshnimiz orqali ingliz, rus yoki o'zbek tilida so'zlashuvchi litsenziyali gidlar bilan bog'lab beramiz."),
    ("Buxoroda xarid qilish uchun nima tavsiya qilasiz?", "Ipak-gilam mahsulotlari, mis buyumlar, milliy kashta va kulolchilik ishlari mashhur suvenirlar hisoblanadi."),
    ("Boshqa shaharlarga (Samarqand, Xiva) kunlik sayohat tashkil qilish mumkinmi?", "Ha, so'rov asosida haydovchi bilan mashina yoki poyezd chiptasi buyurtma qilishda yordam beramiz."),
]

FAQ_STOPWORDS = {
    "qanday","qanaqa","bormi","bo'ladi","bo'ladimi","bo'lsa","bo'lgan","bo'lgani","mumkin",
    "mumkinmi","uchun","bilan","yoki","ham","kerak","necha","nima","qachon","kim",
    "qayerda","qayerdan","qaysi","qancha","olsam","qilsam","qilaman","qilsangiz","qilinadi",
    "kelsam","kelsangiz","bersangiz","qilib","qiling","beramiz","berasiz","berasizlarmi",
    "beriladi","olamiz","oling","olib","turaman","turasiz","turasizlarmi","hisoblanadi",
    "qoysam","qolsam","kutib","tekshiring","yordam","yaqin","yaqinmi","atrofida","atrofda",
    "ichida","tashkil","xizmat","xizmati","xizmatlari","mavjud","mavjudmi","alohida","ravishda",
    "davomida","haqida","tomonidan","bo'ylab","oldin","keyin","o'zi","o'zida","ustuvor",
    "katta","kichik","yaxshi","yomon","yangi","eski","tez","sekin","juda","albatta","balki",
    "lekin","ammo","xayr","salom","salomlar","rahmat","tashakkur","iltimos","mayli","bugun",
    "ertaga","kecha","hozir","hammaga","hamma","bizga","sizga","sizlar","bizlar","qilsangizchi",
}

def _faq_keywords(text):
    text = text.lower().replace("-", "")
    text = re.sub(r"[^a-z0-9Ѐ-ӿ']+", " ", text)
    stems = set()
    for w in text.split():
        w = w.strip("'")
        if len(w) >= 4 and w not in FAQ_STOPWORDS:
            stems.add(w[:5])
    return stems

FAQ_INDEX = [(_faq_keywords(q), a) for q, a in FAQ_LIST]
FAQ_STEM_DF = Counter()
for _kw, _ in FAQ_INDEX:
    for _k in _kw:
        FAQ_STEM_DF[_k] += 1

def find_faq_answer(text, threshold=0.9):
    msg_kw = _faq_keywords(text)
    if not msg_kw:
        return None
    best_score, best_answer = 0.0, None
    for q_kw, answer in FAQ_INDEX:
        common = msg_kw & q_kw
        if not common:
            continue
        score = sum(1.0 / FAQ_STEM_DF[k] for k in common)
        if score > best_score:
            best_score, best_answer = score, answer
    if best_score >= threshold:
        return best_answer
    return None

async def group_auto_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text_lower = update.message.text.lower()
    if update.message.chat.type not in ("group", "supergroup"):
        return
    matched_topic = None
    for keywords, topic in GURUH_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            matched_topic = topic
            break
    if matched_topic:
        reply = reception_faq(matched_topic)
        if reply:
            await update.message.reply_text(reply, parse_mode="Markdown")
        return
    faq_answer = find_faq_answer(update.message.text)
    if faq_answer:
        await update.message.reply_text(faq_answer)


async def health_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌅 Nonushta retsepti",    callback_data="meal_nonushta")],
        [InlineKeyboardButton("☀️ Tushlik retsepti",     callback_data="meal_tushlik")],
        [InlineKeyboardButton("🌙 Kechki ovqat",         callback_data="meal_kechki")],
        [InlineKeyboardButton("🍎 Snack",                callback_data="meal_snack")],
        [InlineKeyboardButton("💪 Qorin mashqlari",      callback_data="mashq_qorin")],
        [InlineKeyboardButton("🚶 Ofis faolligi",        callback_data="mashq_ofis")],
        [InlineKeyboardButton("📋 Oltin qoidalar",       callback_data="qoidalar")],
        [InlineKeyboardButton("⚖️ Vazn yozish",          callback_data="vazn_log")],
        [InlineKeyboardButton("📊 Vazn grafigi",         callback_data="vazn_grafik")],
        [InlineKeyboardButton("🍽 Kunlik menyu",         callback_data="kunlik_menyu")],
    ])
    await update.message.reply_text("🥗 *Sog'liq & Ovqatlanish*\n━━━━━━━━━━━━━━━\nNimani ko'rmoqchisiz?",
        parse_mode="Markdown", reply_markup=kb)
    return MENU

async def health_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = load_data()
    u = get_user(data, update.effective_user.id)
    if q.data.startswith("meal_"):
        meal_type = q.data.replace("meal_", "")
        meal = random.choice(MEALS.get(meal_type, []))
        ingr = "\n".join(f"  • {i}" for i in meal["ingredientlar"])
        msg = (f"*{meal['nom']}*\n\n📊 `{meal['kaloria']} kcal`\n"
               f"💪 {meal['oqsil']} | 🧈 {meal['yog']} | 🌾 {meal['uglevod']}\n\n"
               f"🛒 *Ingredientlar:*\n{ingr}\n\n"
               f"👨‍🍳 *Tayyorlash:*\n{meal['tayyorlash']}\n\n"
               f"✅ {meal['foyda']}")
        kb2 = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Boshqa retsept", callback_data=q.data)]])
        await q.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb2)
    elif q.data.startswith("mashq_"):
        idx = 0 if q.data == "mashq_qorin" else 1
        mashq = MASHQLAR[idx]
        lines = "\n\n".join(f"*{i+1}. {m[0]}*\n📋 {m[1]}\n💡 {m[2]}" for i, m in enumerate(mashq["mashqlar"]))
        await q.message.reply_text(f"{mashq['nom']}\n⏱ {mashq['vaqt']}\n\n{lines}", parse_mode="Markdown")
    elif q.data == "qoidalar":
        lines = "\n".join(f"{i+1}. {q_}" for i, q_ in enumerate(QOIDALAR))
        await q.message.reply_text(f"📋 *Oltin qoidalar*\n\n{lines}", parse_mode="Markdown")
    elif q.data == "vazn_log":
        await q.message.reply_text("⚖️ Bugungi vazningizni kiriting (kg):\nMisol: `82.5`", parse_mode="Markdown")
        return WEIGHT_LOG
    elif q.data == "vazn_grafik":
        logs = u.get("weight_log", [])
        if len(logs) < 2:
            await q.message.reply_text("📭 Kamida 2 ta yozuv kerak."); return MENU
        max_v = max(l["kg"] for l in logs); min_v = min(l["kg"] for l in logs)
        lines = [f"`{l['date']}` {'█'*int((l['kg']-min_v+0.5)/((max_v-min_v+1))*10)} `{l['kg']} kg`" for l in logs[-14:]]
        diff = logs[-1]["kg"] - logs[0]["kg"]
        await q.message.reply_text(f"⚖️ *Vazn grafigi*\n\n" + "\n".join(lines) +
            f"\n\n{'📉' if diff<0 else '📈'} {abs(diff):.1f} kg", parse_mode="Markdown")
    elif q.data == "kunlik_menyu":
        n=random.choice(MEALS["nonushta"]); t=random.choice(MEALS["tushlik"])
        k=random.choice(MEALS["kechki"]); s=random.choice(MEALS["snack"])
        total=n["kaloria"]+t["kaloria"]+k["kaloria"]+s["kaloria"]
        msg=(f"🍽 *Kunlik menyu* — `{total} kcal`\n\n"
             f"🌅 {n['nom']} ({n['kaloria']} kcal)\n☀️ {t['nom']} ({t['kaloria']} kcal)\n"
             f"🍎 {s['nom']} ({s['kaloria']} kcal)\n🌙 {k['nom']} ({k['kaloria']} kcal)")
        await q.message.reply_text(msg, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Boshqa menyu", callback_data="kunlik_menyu")]]))
    return MENU

async def weight_log_save(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try: kg = float(update.message.text.replace(",","."))
    except:
        await update.message.reply_text("❌ Masalan: `82.5`", parse_mode="Markdown"); return WEIGHT_LOG
    data = load_data(); u = get_user(data, update.effective_user.id)
    today = datetime.date.today().strftime("%d.%m")
    if not u.get("weight_log"): u["weight_log"] = []
    if u["weight_log"] and u["weight_log"][-1]["date"] == today:
        u["weight_log"][-1]["kg"] = kg
    else:
        u["weight_log"].append({"date": today, "kg": kg})
    save_data(data)
    await update.message.reply_text(f"✅ *{kg} kg* yozildi!", parse_mode="Markdown", reply_markup=MAIN_KB)
    return MENU

async def hotel_income_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏨 Qaysi mehmonxona?", reply_markup=hotel_kb()); return HOTEL_SELECT

async def hotel_select(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if txt == "🔙 Orqaga":
        await update.message.reply_text("Asosiy menyu:", reply_markup=MAIN_KB); return MENU
    if txt not in HOTELS:
        await update.message.reply_text("Menyudan tanlang:", reply_markup=hotel_kb()); return HOTEL_SELECT
    ctx.user_data["selected_hotel"] = txt
    await update.message.reply_text(f"*{txt}*\n\n💵 Daromad (so'mda):", parse_mode="Markdown"); return HOTEL_AMOUNT

async def hotel_amount_save(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try: amount = float(update.message.text.replace(",","").replace(" ",""))
    except: await update.message.reply_text("❌ Noto'g'ri son:"); return HOTEL_AMOUNT
    data = load_data(); u = get_user(data, update.effective_user.id)
    hotel = ctx.user_data.get("selected_hotel","Noma'lum")
    today = datetime.date.today().strftime("%d.%m.%Y")
    month = datetime.date.today().strftime("%Y-%m")
    u["balance"] += amount; u["income"] += amount
    u["hotel_income"][hotel] = u["hotel_income"].get(hotel,0) + amount
    if month not in u["monthly_hotels"]: u["monthly_hotels"][month] = {}
    u["monthly_hotels"][month][hotel] = u["monthly_hotels"][month].get(hotel,0) + amount
    u["transactions"].append({"type":"income","amount":amount,"category":hotel,"date":today,"month":month})
    save_data(data)
    top = max(u["hotel_income"], key=u["hotel_income"].get)
    await update.message.reply_text(
        f"✅ *{hotel}*\n`{amount:,.0f} so'm`\n💼 Balans: `{u['balance']:,.0f}`\n🏆 Top: *{top}*",
        parse_mode="Markdown", reply_markup=MAIN_KB); return MENU

async def other_income_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 Daromad turi:", reply_markup=income_kb()); return INCOME_CAT

async def income_cat_select(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if txt == "🔙 Orqaga":
        await update.message.reply_text("Asosiy menyu:", reply_markup=MAIN_KB); return MENU
    if txt not in INCOME_CATS:
        await update.message.reply_text("Menyudan tanlang:", reply_markup=income_kb()); return INCOME_CAT
    ctx.user_data["income_cat"] = txt
    await update.message.reply_text(f"*{txt}* miqdori:", parse_mode="Markdown"); return INCOME_AMOUNT

async def other_income_save(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try: amount = float(update.message.text.replace(",","").replace(" ",""))
    except: await update.message.reply_text("❌ Noto'g'ri:"); return INCOME_AMOUNT
    data = load_data(); u = get_user(data, update.effective_user.id)
    cat = ctx.user_data.get("income_cat","💼 Boshqa")
    today = datetime.date.today().strftime("%d.%m.%Y"); month = datetime.date.today().strftime("%Y-%m")
    u["balance"] += amount; u["income"] += amount
    u["transactions"].append({"type":"income","amount":amount,"category":cat,"date":today,"month":month})
    save_data(data)
    await update.message.reply_text(f"✅ *{cat}*\n`{amount:,.0f} so'm`\n💼 Balans: `{u['balance']:,.0f}`",
        parse_mode="Markdown", reply_markup=MAIN_KB); return MENU

async def expense_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 Kategoriya:", reply_markup=expense_kb()); return EXPENSE_CAT

async def expense_cat_select(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if txt == "🔙 Orqaga":
        await update.message.reply_text("Asosiy menyu:", reply_markup=MAIN_KB); return MENU
    if txt not in EXPENSE_CATS:
        await update.message.reply_text("Menyudan tanlang:", reply_markup=expense_kb()); return EXPENSE_CAT
    ctx.user_data["expense_cat"] = txt
    await update.message.reply_text(f"*{txt}* miqdori:", parse_mode="Markdown"); return EXPENSE_AMOUNT

async def expense_amount_save(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try: amount = float(update.message.text.replace(",","").replace(" ",""))
    except: await update.message.reply_text("❌ Noto'g'ri:"); return EXPENSE_AMOUNT
    data = load_data(); u = get_user(data, update.effective_user.id)
    cat = ctx.user_data.get("expense_cat","Boshqa")
    today = datetime.date.today().strftime("%d.%m.%Y"); month = datetime.date.today().strftime("%Y-%m")
    u["balance"] -= amount; u["expense"] += amount
    u["transactions"].append({"type":"expense","amount":amount,"category":cat,"date":today,"month":month})
    save_data(data)
    await update.message.reply_text(f"✅ *{cat}*\n`{amount:,.0f} so'm`\n💼 Balans: `{u['balance']:,.0f}`",
        parse_mode="Markdown", reply_markup=MAIN_KB); return MENU

async def show_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data(); u = get_user(data, update.effective_user.id)
    today = datetime.date.today().strftime("%d.%m.%Y")
    msg = (f"💼 *Moliyaviy holat* — {today}\n"
           f"━━━━━━━━━━━━━━━\n\n"
           f"💚 Daromad: `{u['income']:,.0f} so'm`\n"
           f"❤️ Xarajat: `{u['expense']:,.0f} so'm`\n"
           f"━━━━━━━━━━━━━━━\n"
           f"💰 Balans: `{u['balance']:,.0f} so'm`")
    if u["hotel_income"]:
        total = sum(u["hotel_income"].values())
        top3 = sorted(u["hotel_income"].items(), key=lambda x:-x[1])[:3]
        msg += "\n\n🏨 *Top mehmonxonalar:*\n"
        for i,(h,v) in enumerate(top3):
            msg += f"{'🥇🥈🥉'[i]} {h}: `{v:,.0f}` ({v/total*100:.0f}%)\n"
    msg += expense_advice(u)
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_KB); return MENU

def build_bar(value, max_val, width=10):
    if max_val == 0: return "░"*width
    return "█"*int((value/max_val)*width) + "░"*(width-int((value/max_val)*width))

def expense_advice(u):
    month = datetime.date.today().strftime("%Y-%m")
    cats = {}
    for t in u["transactions"]:
        if t["type"] == "expense" and t.get("month") == month:
            cats[t["category"]] = cats.get(t["category"], 0) + t["amount"]
    if not cats:
        return ""
    total_exp = sum(cats.values())
    top_cat, top_val = max(cats.items(), key=lambda x: x[1])
    pct = (top_val/total_exp*100) if total_exp else 0
    msg = (f"\n\n⚠️ *Tavsiya:* Bu oyda eng ko'p xarajat — *{top_cat}* "
           f"(`{top_val:,.0f} so'm`, {pct:.0f}%). Shu toifani kamaytirishga harakat qiling.")
    if u["expense"] > u["income"]:
        msg += "\n🔴 *Diqqat:* umumiy xarajatlaringiz daromadingizdan oshib ketmoqda!"
    budget = u.get("budget_limit", 0)
    if budget and total_exp > budget:
        msg += f"\n🟠 Bu oy byudjetdan (`{budget:,.0f}`) `{total_exp-budget:,.0f} so'm` oshib ketdingiz."
    return msg

async def show_graph(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏨 Mehmonxona reytingi", callback_data="graph_hotels")],
        [InlineKeyboardButton("📅 Kunlik daromad",      callback_data="graph_daily")],
        [InlineKeyboardButton("📆 Oylik taqqoslama",    callback_data="graph_monthly")],
        [InlineKeyboardButton("💸 Xarajat taqsimoti",  callback_data="graph_expense")],
    ])
    await update.message.reply_text("📈 *Grafik*\n━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=kb); return MENU

async def graph_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    data = load_data(); u = get_user(data, update.effective_user.id)
    if q.data == "graph_hotels":
        hi = u.get("hotel_income",{})
        if not hi: await q.message.reply_text("📭 Ma'lumot yo'q."); return MENU
        total = sum(hi.values()); sorted_h = sorted(hi.items(), key=lambda x:-x[1]); max_v = sorted_h[0][1]
        lines = [f"{'🥇🥈🥉'[i] if i<3 else str(i+1)+'.'} *{h.replace('🏨 ','')}*\n`{build_bar(v,max_v,12)}` {v/total*100:.0f}%\n`{v:,.0f}`\n"
                 for i,(h,v) in enumerate(sorted_h)]
        await q.message.reply_text(f"🏆 *Reyting*\nJami: `{total:,.0f}`\n\n" + "\n".join(lines), parse_mode="Markdown")
    elif q.data == "graph_daily":
        today = datetime.date.today()
        daily = {(today-datetime.timedelta(days=i)).strftime("%d.%m.%Y"): 0 for i in range(13,-1,-1)}
        for t in u["transactions"]:
            if t["type"]=="income" and t["date"] in daily: daily[t["date"]] += t["amount"]
        max_v = max(daily.values()) or 1
        lines = [f"`{d[:5]}` {build_bar(v,max_v,10)} `{v/1000:.0f}k`" for d,v in daily.items()]
        await q.message.reply_text("📅 *Kunlik daromad*\n\n" + "\n".join(lines), parse_mode="Markdown")
    elif q.data == "graph_monthly":
        monthly = {}
        for t in u["transactions"]:
            m = t.get("month","?")
            monthly.setdefault(m, {"income":0,"expense":0})
            monthly[m][t["type"]] += t["amount"]
        if not monthly: await q.message.reply_text("📭 Ma'lumot yo'q."); return MENU
        months = sorted(monthly.keys())[-6:]
        max_v = max(max(monthly[m]["income"], monthly[m]["expense"]) for m in months) or 1
        lines = [f"`{m}`\n💚{build_bar(monthly[m]['income'],max_v,10)} `{monthly[m]['income']:,.0f}`\n"
                 f"❤️{build_bar(monthly[m]['expense'],max_v,10)} `{monthly[m]['expense']:,.0f}`"
                 for m in months]
        await q.message.reply_text("📆 *Oylik taqqoslama*\n\n" + "\n\n".join(lines), parse_mode="Markdown")
    elif q.data == "graph_expense":
        cats = {}
        for t in u["transactions"]:
            if t["type"]=="expense": cats[t["category"]]=cats.get(t["category"],0)+t["amount"]
        if not cats: await q.message.reply_text("📭 Xarajat yo'q."); return MENU
        total = sum(cats.values()); max_v = max(cats.values())
        lines = [f"{c}\n`{build_bar(v,max_v,10)}` {v/total*100:.0f}% — `{v:,.0f}`\n"
                 for c,v in sorted(cats.items(),key=lambda x:-x[1])]
        await q.message.reply_text(f"💸 *Xarajatlar*\nJami: `{total:,.0f}`\n\n" + "\n".join(lines), parse_mode="Markdown")
    return MENU

async def show_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Bugun", callback_data="rep_today"),
         InlineKeyboardButton("📆 Bu oy", callback_data="rep_month")],
        [InlineKeyboardButton("🏨 Mehmonxonalar", callback_data="rep_hotels")],
        [InlineKeyboardButton("📋 Oxirgi 10 ta",  callback_data="rep_last10")],
    ])
    await update.message.reply_text("📊 *Hisobot*\n━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=kb); return MENU

async def report_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    data = load_data(); u = get_user(data, update.effective_user.id)
    today = datetime.date.today().strftime("%d.%m.%Y"); month = datetime.date.today().strftime("%Y-%m")
    if q.data == "rep_today":
        txs = [t for t in u["transactions"] if t["date"]==today]
        if not txs: await q.message.reply_text("📭 Bugun yozuv yo'q."); return MENU
        inc=sum(t["amount"] for t in txs if t["type"]=="income"); exp=sum(t["amount"] for t in txs if t["type"]=="expense")
        lines="\n".join(f"{'🟢' if t['type']=='income' else '🔴'} {t['category']} `{t['amount']:,.0f}`" for t in txs)
        await q.message.reply_text(f"📅 *{today}*\n\n{lines}\n\n💚`{inc:,.0f}` ❤️`{exp:,.0f}`", parse_mode="Markdown")
    elif q.data == "rep_month":
        txs=[t for t in u["transactions"] if t.get("month","")==month]
        if not txs: await q.message.reply_text("📭 Bu oyda yozuv yo'q."); return MENU
        inc=sum(t["amount"] for t in txs if t["type"]=="income"); exp=sum(t["amount"] for t in txs if t["type"]=="expense")
        await q.message.reply_text(f"📆 *{month}*\n💚`{inc:,.0f}` ❤️`{exp:,.0f}`\n💰Sof: `{inc-exp:,.0f}`", parse_mode="Markdown")
    elif q.data == "rep_hotels":
        hi=u.get("hotel_income",{})
        if not hi: await q.message.reply_text("📭 Yo'q."); return MENU
        total=sum(hi.values())
        lines="\n".join(f"  {h}\n  └ `{v:,.0f}` ({v/total*100:.1f}%)" for h,v in sorted(hi.items(),key=lambda x:-x[1]))
        await q.message.reply_text(f"🏨 *Mehmonxonalar:*\n\n{lines}\n\n💰`{total:,.0f}`", parse_mode="Markdown")
    elif q.data == "rep_last10":
        txs=u["transactions"][-10:]
        if not txs: await q.message.reply_text("📭 Yozuv yo'q."); return MENU
        lines="\n".join(f"{'🟢' if t['type']=='income' else '🔴'} {t['date']} {t['category']} `{t['amount']:,.0f}`" for t in reversed(txs))
        await q.message.reply_text(f"📋 *Oxirgi 10:*\n\n{lines}", parse_mode="Markdown")
    return MENU

async def show_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data=load_data(); u=get_user(data,update.effective_user.id)
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("➕ Qo'shish", callback_data="task_add"),
                               InlineKeyboardButton("🗑 Tozalash", callback_data="task_clear")]])
    if not u["tasks"]:
        await update.message.reply_text("📋 Vazifalar bo'sh.", reply_markup=kb); return MENU
    lines="\n".join(f"{'✅' if t.get('done') else '⬜'} {t.get('time','?')} — {t['text']}" for t in u["tasks"])
    await update.message.reply_text(f"📋 *Vazifalar*\n━━━━━━━━━━━━━━━\n\n{lines}", parse_mode="Markdown", reply_markup=kb); return MENU

async def task_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    data=load_data(); u=get_user(data,update.effective_user.id)
    if q.data=="task_add":
        await q.message.reply_text("✏️ Vazifa matnini yozing:"); return TASK_TEXT
    elif q.data=="task_clear":
        u["tasks"]=[]; save_data(data); await q.message.reply_text("🗑 Tozalandi.", reply_markup=MAIN_KB)
    return MENU

async def task_text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["task_text"]=update.message.text
    await update.message.reply_text("⏰ Vaqt (HH:MM):"); return TASK_TIME

async def task_time_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    t=update.message.text.strip()
    try: datetime.datetime.strptime(t,"%H:%M")
    except: await update.message.reply_text("❌ Format: HH:MM"); return TASK_TIME
    data=load_data(); u=get_user(data,update.effective_user.id)
    u["tasks"].append({"text":ctx.user_data["task_text"],"time":t,"done":False})
    u["tasks"].sort(key=lambda x:x["time"]); save_data(data)
    await update.message.reply_text(f"✅ *{ctx.user_data['task_text']}* — {t}", parse_mode="Markdown", reply_markup=MAIN_KB); return MENU

async def show_schedule(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    today=datetime.date.today()
    wdays=["Dushanba","Seshanba","Chorshanba","Payshanba","Juma","Shanba","Yakshanba"]
    msg=(f"📅 *{today.strftime('%d.%m.%Y')} — {wdays[today.weekday()]}*\n"
         f"━━━━━━━━━━━━━━━\n\n"
         f"🌅 07:00 — Vazn o'lchash\n  07:15 — Mashqlar\n  08:00 — Nonushta\n\n"
         f"☀️ 12:00 — Daromad kiritish\n  13:00 — Tushlik\n\n"
         f"🌆 17:00 — Xarajat kiritish\n  19:00 — Kechki ovqat\n  20:00 — 🚫 Ovqat tugaydi\n  22:00 — 😴 Uxlash")
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_KB); return MENU

async def settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data=load_data(); u=get_user(data,update.effective_user.id)
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("💰 Byudjet", callback_data="set_budget"),
                               InlineKeyboardButton("🗑 Tozalash", callback_data="clear_all")]])
    await update.message.reply_text(f"⚙️ *Sozlamalar*\n━━━━━━━━━━━━━━━\n💰 Byudjet: `{u['budget_limit']:,.0f}`",
        parse_mode="Markdown", reply_markup=kb); return MENU

async def settings_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    data=load_data(); u=get_user(data,update.effective_user.id)
    if q.data=="set_budget":
        await q.message.reply_text("💰 Oylik byudjet miqdori:"); return BUDGET_SET
    elif q.data=="clear_all":
        u.update({"balance":0,"income":0,"expense":0,"transactions":[],"tasks":[],"hotel_income":{},"monthly_hotels":{},"weight_log":[]})
        save_data(data); await q.message.reply_text("🗑 Tozalandi.", reply_markup=MAIN_KB)
    return MENU

async def budget_set(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try: limit=float(update.message.text.replace(",","").replace(" ",""))
    except: await update.message.reply_text("❌ Noto'g'ri:"); return BUDGET_SET
    data=load_data(); u=get_user(data,update.effective_user.id); u["budget_limit"]=limit; save_data(data)
    await update.message.reply_text(f"✅ Byudjet: `{limit:,.0f}`", parse_mode="Markdown", reply_markup=MAIN_KB); return MENU

async def morning_reminder(app):
    data=load_data(); today=datetime.date.today()
    meal=random.choice(MEALS["nonushta"]); tip=random.choice(QOIDALAR)
    for uid,u in data.items():
        try:
            msg=(f"🌅 *Xayrli tong!* — {today.strftime('%d.%m.%Y')}\n\n"
                 f"💼 Balans: `{u['balance']:,.0f} so'm`\n\n"
                 f"🌅 *Nonushta:* {meal['nom']} — `{meal['kaloria']} kcal`\n\n"
                 f"💡 *Maslahat:* {tip}")
            await app.bot.send_message(chat_id=int(uid), text=msg, parse_mode="Markdown")
        except: pass

async def evening_checkin(app):
    data=load_data(); today=datetime.date.today().strftime("%d.%m.%Y")
    for uid,u in data.items():
        try:
            inc=sum(t["amount"] for t in u.get("transactions",[]) if t["date"]==today and t["type"]=="income")
            exp=sum(t["amount"] for t in u.get("transactions",[]) if t["date"]==today and t["type"]=="expense")
            meal=random.choice(MEALS["kechki"])
            msg=(f"🌆 *Kechki tekshiruv* — {today}\n\n"
                 f"💚 Daromad: `{inc:,.0f}`\n❤️ Xarajat: `{exp:,.0f}`\n\n"
                 f"🌙 *Kechki ovqat:* {meal['nom']} — `{meal['kaloria']} kcal`\n\n"
                 f"🚫 20:00 dan keyin ovqat emang!")
            await app.bot.send_message(chat_id=int(uid), text=msg, parse_mode="Markdown")
        except: pass

async def fallback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Menyudan tanlang:", reply_markup=MAIN_KB); return MENU

async def post_init(app):
    scheduler=AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(morning_reminder,"cron",hour=9,minute=0,args=[app])
    scheduler.add_job(evening_checkin,"cron",hour=18,minute=0,args=[app])
    scheduler.start()
    print("🔔 Eslatmalar yoqildi: 09:00 | 18:00")

def main():
    app=Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    conv=ConversationHandler(
        entry_points=[CommandHandler("start",start)],
        states={
            MENU:[
                MessageHandler(filters.Regex("🏨 Mehmonxona daromad"),hotel_income_start),
                MessageHandler(filters.Regex("💸 Xarajat"),expense_start),
                MessageHandler(filters.Regex("➕ Boshqa daromad"),other_income_start),
                MessageHandler(filters.Regex("💰 Balans"),show_balance),
                MessageHandler(filters.Regex("📊 Hisobot"),show_report),
                MessageHandler(filters.Regex("📈 Grafik"),show_graph),
                MessageHandler(filters.Regex("🥗 Ovqat & Sog'liq"),health_menu),
                MessageHandler(filters.Regex("📅 Kun tartibi"),show_schedule),
                MessageHandler(filters.Regex("✅ Vazifalar"),show_tasks),
                MessageHandler(filters.Regex("⚙️ Sozlamalar"),settings),
                MessageHandler(filters.Regex("🛎️ Reception Bot"),reception_menu),
                MessageHandler(filters.Regex("📞 Aloqa"),contact_info),
                CallbackQueryHandler(graph_callback,pattern="^graph_"),
                CallbackQueryHandler(report_callback,pattern="^rep_"),
                CallbackQueryHandler(health_callback,pattern="^(meal_|mashq_|qoidalar|vazn_|kunlik_menyu)"),
                CallbackQueryHandler(task_callback,pattern="^(task_add|task_clear)"),
                CallbackQueryHandler(settings_callback,pattern="^(set_budget|clear_all)$"),
                CallbackQueryHandler(reception_callback,pattern="^rec_"),
            ],
            HOTEL_SELECT:[MessageHandler(filters.TEXT&~filters.COMMAND,hotel_select)],
            HOTEL_AMOUNT:[MessageHandler(filters.TEXT&~filters.COMMAND,hotel_amount_save)],
            INCOME_CAT:[MessageHandler(filters.TEXT&~filters.COMMAND,income_cat_select)],
            INCOME_AMOUNT:[MessageHandler(filters.TEXT&~filters.COMMAND,other_income_save)],
            EXPENSE_CAT:[MessageHandler(filters.TEXT&~filters.COMMAND,expense_cat_select)],
            EXPENSE_AMOUNT:[MessageHandler(filters.TEXT&~filters.COMMAND,expense_amount_save)],
            TASK_TEXT:[MessageHandler(filters.TEXT&~filters.COMMAND,task_text_handler)],
            TASK_TIME:[MessageHandler(filters.TEXT&~filters.COMMAND,task_time_handler)],
            BUDGET_SET:[MessageHandler(filters.TEXT&~filters.COMMAND,budget_set)],
            WEIGHT_LOG:[MessageHandler(filters.TEXT&~filters.COMMAND,weight_log_save)],
        },
        fallbacks=[MessageHandler(filters.ALL,fallback)],
        allow_reentry=True
    )
    app.add_handler(conv)
    app.add_handler(MessageHandler(
        filters.TEXT&~filters.COMMAND&(filters.ChatType.GROUP|filters.ChatType.SUPERGROUP),
        group_auto_reply
    ))
    print("✅ Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__=="__main__":
    main()
