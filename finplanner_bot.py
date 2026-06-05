"""
FinPlanner Pro MAX — Mehmonxona + Moliya + Sog'liq + Retseptlar + Reception Bot
"""

import os, json, datetime, random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = "8804626503:AAGJZq3EyaXrqyHrPw3ZHMt1fOUS7IU8lDU"
DATA_FILE  = "data.json"

HOTELS = [
    "🏨 Golden Degrez Hotel",
    "🏨 Buxoro Air Hotel",
    "🏨 Anor Hotel",
    "🏨 Muxsin Hotel",
    "🏨 Temur Hotel",
    "🏨 Al Buxari Hotel",
    "🏨 Al Fayz Hotel",
]

EXPENSE_CATS = [
    "💧 Suv", "⚡ Elektr", "🔥 Gaz", "🌐 Internet",
    "🍔 Ovqat", "🚌 Transport", "🏥 Sog'liq",
    "🛍 Xarid", "📚 Ta'lim", "🏠 Uy xarajat",
    "🔧 Ta'mirlash", "👷 Ish haqi", "📦 Boshqa", "🔙 Orqaga"
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
            "⚠️ *MUHIM:*\nXonaga kirish uchun asl *PASPORT* talab qilinadi!\n"
            "ID karta qabul qilinmaydi. 🪪"
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
            "Xona faqat *asl PASPORT* asosida beriladi.\n\n"
            "❌ Qabul qilinmaydi:\n  • ID karta\n  • Haydovchilik guvohnomasi\n\n"
            "✅ Faqat asl pasport qabul qilinadi."
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
 INCOME_AMOUNT, EXPENSE_CAT, EXPENSE_AMOUNT,
 TASK_TEXT, TASK_TIME, BUDGET_SET, WEIGHT_LOG) = range(10)

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

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    get_user(data, update.effective_user.id)
    save_data(data)
    await update.message.reply_text(
        f"Assalomu alaykum, *{update.effective_user.first_name}*! 👋\n\n"
        "🏨 *FinPlanner Pro MAX*\n\n"
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
        "🛎️ *Mehmonxona Reception Bot*\n\n"
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
    if not matched_topic:
        return
    reply = reception_faq(matched_topic)
    if reply:
        await update.message.reply_text(reply, parse_mode="Markdown")

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
    await update.message.reply_text("🥗 *Sog'liq & Ovqatlanish*\nNimani ko'rmoqchisiz?",
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
    await update.message.reply_text("💵 Daromad miqdori:"); return INCOME_AMOUNT

async def other_income_save(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try: amount = float(update.message.text.replace(",","").replace(" ",""))
    except: await update.message.reply_text("❌ Noto'g'ri:"); return INCOME_AMOUNT
    data = load_data(); u = get_user(data, update.effective_user.id)
    today = datetime.date.today().strftime("%d.%m.%Y"); month = datetime.date.today().strftime("%Y-%m")
    u["balance"] += amount; u["income"] += amount
    u["transactions"].append({"type":"income","amount":amount,"category":"💼 Boshqa","date":today,"month":month})
    save_data(data)
    await update.message.reply_text(f"✅ `{amount:,.0f} so'm`\n💼 Balans: `{u['balance']:,.0f}`",
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
    msg = (f"💼 *Moliyaviy holat* — {today}\n\n"
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
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_KB); return MENU

def build_bar(value, max_val, width=10):
    if max_val == 0: return "░"*width
    return "█"*int((value/max_val)*width) + "░"*(width-int((value/max_val)*width))

async def show_graph(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏨 Mehmonxona reytingi", callback_data="graph_hotels")],
        [InlineKeyboardButton("📅 Kunlik daromad",      callback_data="graph_daily")],
        [InlineKeyboardButton("📆 Oylik taqqoslama",    callback_data="graph_monthly")],
        [InlineKeyboardButton("💸 Xarajat taqsimoti",  callback_data="graph_expense")],
    ])
    await update.message.reply_text("📈 *Grafik:*", parse_mode="Markdown", reply_markup=kb); return MENU

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
    await update.message.reply_text("📊 *Hisobot:*", parse_mode="Markdown", reply_markup=kb); return MENU

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
    await update.message.reply_text(f"📋 *Vazifalar*\n\n{lines}", parse_mode="Markdown", reply_markup=kb); return MENU

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
    msg=(f"📅 *{today.strftime('%d.%m.%Y')} — {wdays[today.weekday()]}*\n\n"
         f"🌅 07:00 — Vazn o'lchash\n  07:15 — Mashqlar\n  08:00 — Nonushta\n\n"
         f"☀️ 12:00 — Daromad kiritish\n  13:00 — Tushlik\n\n"
         f"🌆 17:00 — Xarajat kiritish\n  19:00 — Kechki ovqat\n  20:00 — 🚫 Ovqat tugaydi\n  22:00 — 😴 Uxlash")
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_KB); return MENU

async def settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data=load_data(); u=get_user(data,update.effective_user.id)
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("💰 Byudjet", callback_data="set_budget"),
                               InlineKeyboardButton("🗑 Tozalash", callback_data="clear_all")]])
    await update.message.reply_text(f"⚙️ *Sozlamalar*\n💰 Byudjet: `{u['budget_limit']:,.0f}`",
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
