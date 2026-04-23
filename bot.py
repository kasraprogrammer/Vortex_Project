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

# 📥 ذخیره رسیدها (حل مشکل اصلی تو)
receipts = {}

# ===================== MENUS =====================

def user_menu():
    return ReplyKeyboardMarkup(
        [["🚀 شروع خرید", "📦 سفارشات"]],
        resize_keyboard=True
    )

def admin_menu():
    return ReplyKeyboardMarkup(
        [["📊 آمار", "📥 رسیدها"]],
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
        await update.message.reply_text("🏠 به Vortex Shop خوش آمدی", reply_markup=user_menu())


# ===================== TEXT HANDLER =====================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    # 👤 USER
    if user_id not in ADMIN_IDS:

        if text == "🚀 شروع خرید":
            keyboard = [
                [InlineKeyboardButton("🇳🇱 هلند", callback_data="loc_nl")],
                [InlineKeyboardButton("🇹🇷 ترکیه", callback_data="loc_tr")],
                [InlineKeyboardButton("🇩🇪 آلمان", callback_data="loc_de")]
            ]

            await update.message.reply_text(
                "💎 لوکیشن:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif text == "📦 سفارشات":
            await update.message.reply_text("📦 سفارشی ثبت نشده")

        return

    # 👑 ADMIN
    if user_id in ADMIN_IDS:

        if text == "📊 آمار":
            await update.message.reply_text(f"""
📊 آمار

👥 کاربران: {len(users)}
🛒 سفارشات: {len(orders)}
📥 رسیدها: {len(receipts)}
""")

        elif text == "📥 رسیدها":

            if not receipts:
                await update.message.reply_text("📭 هیچ رسیدی وجود ندارد")
                return

            keyboard = []
            for msg_id, data in receipts.items():
                keyboard.append([
                    InlineKeyboardButton(
                        f"👤 {data['user_id']}",
                        callback_data=f"view_{msg_id}"
                    )
                ])

            await update.message.reply_text(
                "📥 لیست رسیدها:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )


# ===================== ORDER =====================

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    plan = q.data.split("_")[1]

    user_data[user_id] = {"plan": plan}

    price_map = {"1": 400, "2": 800, "3": 1200, "4": 1600, "5": 2000, "10": 4000}
    price = price_map.get(plan, 400)

    orders[user_id] = "pending"
    pending.add(user_id)

    await q.edit_message_text(f"""
📦 فاکتور

💵 قیمت: {price}
💳 کارت: {CARD}

📸 رسید ارسال کن
""")

# ===================== RECEIPT FIX =====================

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    forwarded = await update.message.forward(chat_id=ADMIN_IDS[0])

    receipts[forwarded.message_id] = {
        "user_id": user.id,
        "username": user.username
    }

    await update.message.reply_text("✅ رسید ارسال شد")

# ===================== VIEW RECEIPT =====================

async def view_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    msg_id = int(q.data.split("_")[1])
    data = receipts[msg_id]

    keyboard = [
        [InlineKeyboardButton("✅ تایید", callback_data=f"approve_{msg_id}")],
        [InlineKeyboardButton("❌ رد", callback_data=f"reject_{msg_id}")]
    ]

    await q.edit_message_text(
        f"""
📥 رسید

👤 کاربر: {data['user_id']}
""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===================== APPROVE =====================

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    msg_id = int(q.data.split("_")[1])
    user_id = receipts[msg_id]["user_id"]

    await context.bot.send_message(
        chat_id=user_id,
        text="✅ پرداخت تایید شد"
    )

    del receipts[msg_id]

    await q.edit_message_text("✅ تایید شد")


# ===================== REJECT =====================

async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    msg_id = int(q.data.split("_")[1])
    user_id = receipts[msg_id]["user_id"]

    await context.bot.send_message(
        chat_id=user_id,
        text="❌ پرداخت رد شد"
    )

    del receipts[msg_id]

    await q.edit_message_text("❌ رد شد")


# ===================== RUN =====================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(MessageHandler(filters.PHOTO, receipt))

app.add_handler(CallbackQueryHandler(order, pattern="plan_"))
app.add_handler(CallbackQueryHandler(view_receipt, pattern="view_"))
app.add_handler(CallbackQueryHandler(approve, pattern="approve_"))
app.add_handler(CallbackQueryHandler(reject, pattern="reject_"))

app.run_polling()
