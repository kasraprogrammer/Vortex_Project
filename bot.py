from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8653861753:AAEUuafpUZhmx_INOqR1oDdRgmtohkBaiZo"

ADMIN_IDS = [5231145229, 6225624558]
OWNER_ID = 5231145229

CHANNEL_USERNAME = "@Vortexsshop"
CHANNEL_LINK = "https://t.me/Vortexsshop"

CARD = "6219-8618-0647-8813"

user_data = {}
user_messages = {}

users = set()
orders = {}

# 📥 در انتظار سفارشات
pending_users = {}

# ===================== PRODUCTS =====================

PRODUCTS = {
    "nl": {
        "name": "🇳🇱 هلند",
        "plans": {
            "1": {"gb": 1, "price": 400},
            "2": {"gb": 2, "price": 800},
            "3": {"gb": 3, "price": 1200},
            "5": {"gb": 5, "price": 2000},
            "10": {"gb": 10, "price": 4000},
        }
    },
    "tr": {
        "name": "🇹🇷 ترکیه",
        "plans": {
            "1": {"gb": 1, "price": 350},
            "2": {"gb": 2, "price": 700},
            "3": {"gb": 3, "price": 1100},
            "5": {"gb": 5, "price": 1900},
        }
    },
    "de": {
        "name": "🇩🇪 آلمان",
        "plans": {
            "1": {"gb": 1, "price": 450},
            "2": {"gb": 2, "price": 900},
            "3": {"gb": 3, "price": 1300},
            "5": {"gb": 5, "price": 2100},
        }
    }
}

# ===================== MENUS =====================

def user_menu():
    return ReplyKeyboardMarkup(
        [["🚀 شروع خرید", "📦 سفارشات"]],
        resize_keyboard=True
    )

def admin_menu():
    return ReplyKeyboardMarkup(
        [["📊 آمار", "⏳ در انتظار"]],
        resize_keyboard=True
    )

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ===================== START =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)

    if user_id in ADMIN_IDS:
        await update.message.reply_text("👑 پنل ادمین", reply_markup=admin_menu())
    else:
        await update.message.reply_text("🏠 خوش آمدی", reply_markup=user_menu())

# ===================== LOCATIONS =====================

async def locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    keyboard = [
        [InlineKeyboardButton("🇳🇱 هلند", callback_data="loc_nl")],
        [InlineKeyboardButton("🇹🇷 ترکیه", callback_data="loc_tr")],
        [InlineKeyboardButton("🇩🇪 آلمان", callback_data="loc_de")]
    ]

    await q.edit_message_text(
        "💎 کشور را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===================== PLANS =====================

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    loc = q.data.split("_")[1]
    user_data[q.from_user.id] = {"loc": loc}

    product = PRODUCTS[loc]

    keyboard = []

    for plan_id, data in product["plans"].items():
        keyboard.append([
            InlineKeyboardButton(
                f"{data['gb']}GB - {data['price']} تومان",
                callback_data=f"plan_{plan_id}"
            )
        ])

    await q.edit_message_text(
        f"💎 {product['name']}\nپلن را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===================== ORDER =====================

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    plan_id = q.data.split("_")[1]

    loc = user_data[user_id]["loc"]
    product = PRODUCTS[loc]
    plan = product["plans"][plan_id]

    pending_users[user_id] = {
        "plan": f"{plan['gb']}GB",
        "price": plan["price"],
        "status": "pending",
        "receipt_msg_id": None
    }

    await q.edit_message_text(f"""
📦 فاکتور

🌍 محصول: {product['name']}
📦 حجم: {plan['gb']}GB
💰 قیمت: {plan['price']} تومان

💳 کارت: {CARD}

📸 رسید ارسال کن
""")

# ===================== RECEIPT =====================

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    forwarded = await update.message.forward(chat_id=ADMIN_IDS[0])

    if user.id in pending_users:
        pending_users[user.id]["receipt_msg_id"] = forwarded.message_id

    await update.message.reply_text("✅ رسید ارسال شد")

# ===================== ADMIN PANEL =====================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if user_id not in ADMIN_IDS:
        return

    # 📊 آمار
    if text == "📊 آمار":
        await update.message.reply_text(f"""
📊 آمار

👥 کاربران: {len(users)}
⏳ در انتظار: {len(pending_users)}
""")

    # ⏳ در انتظار
    elif text == "⏳ در انتظار":

        if not pending_users:
            await update.message.reply_text("📭 چیزی وجود ندارد")
            return

        keyboard = []

        for uid, data in pending_users.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"👤 {uid} | {data['plan']}",
                    callback_data=f"pending_{uid}"
                )
            ])

        await update.message.reply_text(
            "⏳ سفارشات:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ===================== VIEW PENDING =====================

async def view_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = int(q.data.split("_")[1])
    data = pending_users[user_id]

    receipt_text = "❌ رسید ندارد"
    if data.get("receipt_msg_id"):
        receipt_text = "📥 رسید ثبت شده"

    keyboard = [
        [InlineKeyboardButton("✅ تایید سفارش", callback_data=f"approve_{user_id}")]
    ]

    await q.edit_message_text(f"""
⏳ سفارش

👤 {user_id}
📦 {data['plan']}
💰 {data['price']}
⏳ در انتظار

{receipt_text}
""", reply_markup=InlineKeyboardMarkup(keyboard))

# ===================== APPROVE =====================

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = int(q.data.split("_")[1])

    if user_id in pending_users:
        del pending_users[user_id]

        await context.bot.send_message(
            chat_id=user_id,
            text="✅ سفارش شما تایید شد\n⏳ منتظر دریافت سرویس باشید"
        )

    await q.edit_message_text("✅ تایید شد")

# ===================== RUN =====================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(MessageHandler(filters.PHOTO, receipt))

app.add_handler(CallbackQueryHandler(locations, pattern="loc_"))
app.add_handler(CallbackQueryHandler(plans, pattern="plan_"))
app.add_handler(CallbackQueryHandler(view_pending, pattern="pending_"))
app.add_handler(CallbackQueryHandler(approve, pattern="approve_"))

app.run_polling()
