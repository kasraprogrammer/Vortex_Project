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
pending = set()

# ===================== KEYS =====================

def user_menu():
    return ReplyKeyboardMarkup(
        [
            ["🚀 شروع خرید"],
            ["📦 سفارشات"]
        ],
        resize_keyboard=True
    )

def admin_menu():
    return ReplyKeyboardMarkup(
        [
            ["📊 آمار", "📥 رسیدها"],
            ["👥 کاربران"]
        ],
        resize_keyboard=True
    )

# ===================== CHECK ADMIN =====================

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ===================== START =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)

    if user_id in ADMIN_IDS:
        await update.message.reply_text("👑 پنل ادمین فعال شد", reply_markup=admin_menu())
    else:
        await update.message.reply_text("🏠 به Vortex Shop خوش آمدی", reply_markup=user_menu())

# ===================== BUTTON HANDLER =====================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    # 👤 USER BUTTONS
    if user_id not in ADMIN_IDS:

        if text == "🚀 شروع خرید":
            keyboard = [
                [InlineKeyboardButton("🇳🇱 هلند", callback_data="loc_nl")],
                [InlineKeyboardButton("🇹🇷 ترکیه", callback_data="loc_tr")],
                [InlineKeyboardButton("🇩🇪 آلمان", callback_data="loc_de")]
            ]
            await update.message.reply_text("💎 لوکیشن رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

        elif text == "📦 سفارشات":
            await update.message.reply_text("📦 هنوز سفارشی ثبت نشده")

        return

    # 👑 ADMIN BUTTONS
    if user_id in ADMIN_IDS:

        if text == "📊 آمار":
            await update.message.reply_text(f"""
📊 آمار سیستم

👥 کاربران: {len(users)}
🛒 سفارشات: {len(orders)}
📥 در انتظار: {len(pending)}
""")

        elif text == "📥 رسیدها":
            await update.message.reply_text("📥 برای دیدن رسیدها از پیام‌های فوروارد استفاده کن")

        elif text == "👥 کاربران":
            await update.message.reply_text(f"👥 کل کاربران: {len(users)}")

# ===================== LOCATIONS =====================

async def locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    keyboard = [
        [InlineKeyboardButton("1GB - 400", callback_data="plan_1")],
        [InlineKeyboardButton("2GB - 800", callback_data="plan_2")],
        [InlineKeyboardButton("3GB - 1200", callback_data="plan_3")],
        [InlineKeyboardButton("5GB - 2000", callback_data="plan_5")]
    ]

    await q.edit_message_text("💎 حجم رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

# ===================== ORDER =====================

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    plan = q.data.split("_")[1]

    price_map = {"1": 400, "2": 800, "3": 1200, "5": 2000}
    price = price_map.get(plan, 400)

    orders[user_id] = "pending"
    pending.add(user_id)

    await q.edit_message_text(f"""
📦 فاکتور

💵 قیمت: {price}
💳 کارت: {CARD}

📸 فقط عکس رسید ارسال کن
""")

# ===================== RECEIPT =====================

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    forwarded = await update.message.forward(chat_id=ADMIN_IDS[0])
    user_messages[forwarded.message_id] = user.id

    await update.message.reply_text("✅ رسید ارسال شد")

# ===================== ADMIN REPLY =====================

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in ADMIN_IDS:
        return

    if not update.message.reply_to_message:
        return

    msg_id = update.message.reply_to_message.message_id

    if msg_id in user_messages:
        target = user_messages[msg_id]

        await context.bot.send_message(
            chat_id=target,
            text=f"📩 پاسخ ادمین:\n\n{update.message.text}"
        )

# ===================== RUN =====================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(CallbackQueryHandler(locations, pattern="loc_"))
app.add_handler(CallbackQueryHandler(order, pattern="plan_"))
app.add_handler(MessageHandler(filters.PHOTO, receipt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))

app.run_polling()
