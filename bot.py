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

# ================= ROLE =================

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_owner(user_id):
    return user_id == OWNER_ID

# ================= MEMBER CHECK =================

async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= HOME =================

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 شروع خرید", callback_data="go_locations")]]

    text = "🏠 به Vortex Shop خوش آمدی"

    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

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

    if is_admin(user_id):
        await update.message.reply_text("👑 پنل ادمین" if not is_owner(user_id) else "👑 پنل OWNER")

    await home(update, context)

# ================= LOCATIONS =================

async def locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    keyboard = [
        [InlineKeyboardButton("🇳🇱 هلند", callback_data="loc_nl")],
        [InlineKeyboardButton("🇹🇷 ترکیه", callback_data="loc_tr")],
        [InlineKeyboardButton("🇩🇪 آلمان", callback_data="loc_de")],
        [InlineKeyboardButton("🔙 خانه", callback_data="home")]
    ]

    await q.edit_message_text("💎 لوکیشن سرویس رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= PLANS =================

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    loc = q.data.split("_")[1]
    user_data[q.from_user.id] = {"loc": loc}

    title = {"de": "آلمان", "nl": "هلند"}.get(loc, "ترکیه")

    plans = [
        ("1GB - 400", "1"),
        ("2GB - 800", "2"),
        ("3GB - 1200", "3"),
        ("4GB - 1600", "4"),
        ("5GB - 2000", "5"),
        ("10GB - 4000", "10"),
    ]

    keyboard = [[InlineKeyboardButton(p[0], callback_data=f"plan_{p[1]}")] for p in plans]
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="go_locations")])

    await q.edit_message_text(
        f"💎 {title}\nحجم سرویس رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= ORDER =================

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    plan = q.data.split("_")[1]

    user_data[user_id]["plan"] = plan

    price_map = {"1": 400, "2": 800, "3": 1200, "4": 1600, "5": 2000, "10": 4000}
    price = price_map[plan]

    await q.edit_message_text(f"""
📦 فاکتور نهایی

♾ حجم : {plan}GB
💵 قیمت : {price} تومان

💳 کارت:
{CARD}

📸 رسید ارسال کن
""")

# ================= FIXED RECEIPT (IMPORTANT) =================

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    for admin in ADMIN_IDS:
        sent = await context.bot.copy_message(
            chat_id=admin,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

        user_messages[sent.message_id] = user.id

    await update.message.reply_text("✅ رسید ارسال شد")

# ================= FIXED ADMIN REPLY =================

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not is_admin(user_id):
        return

    if not update.message.reply_to_message:
        return

    replied_id = update.message.reply_to_message.message_id

    if replied_id not in user_messages:
        return

    target_user = user_messages[replied_id]
    msg = update.message.text

    await context.bot.send_message(
        chat_id=target_user,
        text=f"📩 پاسخ ادمین:\n\n{msg}"
    )

    if user_id != OWNER_ID:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"""
📡 لاگ پیام

👤 ادمین: {user_id}
🎯 کاربر: {target_user}

💬 پیام:
{msg}
"""
        )

# ================= RUN =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("home", home))

app.add_handler(CallbackQueryHandler(locations, pattern="go_locations"))
app.add_handler(CallbackQueryHandler(plans, pattern="loc_"))
app.add_handler(CallbackQueryHandler(order, pattern="plan_"))

app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receipt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))

app.run_polling()
