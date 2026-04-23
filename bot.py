from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8653861753:AAEUuafpUZhmx_INOqR1oDdRgmtohkBaiZo"

ADMIN_IDS = [5231145229, 6225624558]
OWNER_ID = 5231145229

CHANNEL_USERNAME = "@Vortexsshop"
CHANNEL_LINK = "https://t.me/Vortexsshop"

CARD = "6219-8618-0647-8813"

user_data = {}
user_messages = {}

# 📊 دیتابیس ساده در RAM
users = set()
orders = {}
pending = set()
approved = set()
completed = set()


def is_admin(user_id):
    return user_id in ADMIN_IDS


async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# 🏠 HOME
async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 شروع خرید", callback_data="go_locations")]]

    text = "🏠 به Vortex Shop خوش آمدی"

    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    users.add(user_id)  # 👈 ثبت کاربر

    if not await is_member(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join")]
        ]

        await update.message.reply_text(
            "⚠️ برای استفاده باید عضو کانال باشی:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await home(update, context)


# 📍 لوکیشن‌ها
async def locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    keyboard = [
        [InlineKeyboardButton("🇳🇱 هلند", callback_data="loc_nl")],
        [InlineKeyboardButton("🇹🇷 ترکیه", callback_data="loc_tr")],
        [InlineKeyboardButton("🇩🇪 آلمان", callback_data="loc_de")],
        [InlineKeyboardButton("🔙 خانه", callback_data="home")]
    ]

    await q.edit_message_text("💎 لوکیشن:", reply_markup=InlineKeyboardMarkup(keyboard))


# 📦 پلن
async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    loc = q.data.split("_")[1]
    user_data[q.from_user.id] = {"loc": loc}

    plans = [
        ("1GB - 400", "1"),
        ("2GB - 800", "2"),
        ("3GB - 1200", "3"),
        ("4GB - 1600", "4"),
        ("5GB - 2000", "5"),
        ("10GB - 4000", "10"),
    ]

    keyboard = [[InlineKeyboardButton(p[0], callback_data=f"plan_{p[1]}")] for p in plans]

    await q.edit_message_text("💎 انتخاب حجم:", reply_markup=InlineKeyboardMarkup(keyboard))


# 🧾 سفارش
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    plan = q.data.split("_")[1]

    user_data[user_id]["plan"] = plan

    price_map = {"1": 400, "2": 800, "3": 1200, "4": 1600, "5": 2000, "10": 4000}
    price = price_map[plan]

    orders[user_id] = "pending"
    pending.add(user_id)

    text = f"""
📦 فاکتور

💵 قیمت: {price} تومان
💳 کارت: {CARD}

📸 رسید ارسال کن
"""

    await q.edit_message_text(text)


# 📥 رسید
async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    forwarded = await update.message.forward(chat_id=ADMIN_IDS[0])

    for admin in ADMIN_IDS[1:]:
        await context.bot.forward_message(
            chat_id=admin,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

    user_messages[forwarded.message_id] = user.id

    await update.message.reply_text("✅ رسید ارسال شد")


# 💬 ریپلای ادمین
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not is_admin(user_id):
        return

    if not update.message.reply_to_message:
        return

    replied_id = update.message.reply_to_message.message_id

    if replied_id in user_messages:
        target_user = user_messages[replied_id]

        msg = update.message.text

        await context.bot.send_message(
            chat_id=target_user,
            text=f"📩 پاسخ:\n\n{msg}"
        )


# 📊 داشبورد OWNER
async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id != OWNER_ID:
        return

    text = f"""
📊 داشبورد فروش

👥 کاربران: {len(users)}
🛒 سفارش‌ها: {len(orders)}
📥 رسیدهای ارسال‌شده: {len(pending) + len(approved)}
⏳ تایید نشده: {len(pending)}
✅ تایید شده: {len(approved)}
📦 تکمیل شده: {len(completed)}
"""

    await update.message.reply_text(text)


# 🚫 محدود کردن کاربر
async def block_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    if update.message.photo:
        return

    if update.message.text and update.message.text.startswith("/start"):
        return

    await update.message.delete()


# 🚀 اجرا
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("home", home))
app.add_handler(CommandHandler("stats", owner_stats))  # 👑 داشبورد

app.add_handler(CallbackQueryHandler(locations, pattern="go_locations"))
app.add_handler(CallbackQueryHandler(plans, pattern="loc_"))
app.add_handler(CallbackQueryHandler(order, pattern="plan_"))

app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receipt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))

app.add_handler(MessageHandler(filters.ALL, block_user_messages), group=1)

app.run_polling()
