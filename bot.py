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

RULES_TEXT = """📜 قوانین و مقررات استفاده از سرویس
━━━━━━━━━━━━━━━━━━━━━━
...
با زدن دکمه "✅ می‌پذیرم" تأیید می‌کنی که قوانین را خوانده‌ای.
"""

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 شروع خرید", callback_data="go_locations")]]
    text = "🏠 به Vortex Shop خوش آمدی"

    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

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

    keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]

    await update.message.reply_text(
        RULES_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id

    if await is_member(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]
        await q.edit_message_text(RULES_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await q.answer("❌ هنوز عضو کانال نشدی!", show_alert=True)

async def accept_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    keyboard = [[InlineKeyboardButton("🚀 شروع خرید", callback_data="go_locations")]]

    await q.edit_message_text(
        "✅ قوانین پذیرفته شد\n\nحالا میتونی خریدت رو شروع کنی 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    loc = q.data.split("_")[1]
    user_data[q.from_user.id] = {"loc": loc}

    title = {"de": "آلمان", "nl": "هلند", "tr": "ترکیه"}.get(loc, "سرویس")

    plans = [
        ("1GB - 369", "1"),
        ("2GB - 738", "2"),
        ("3GB - 1107", "3"),
        ("4GB - 1476", "4"),
        ("5GB - 1845", "5"),
        ("10GB - 3690", "10"),
    ]

    keyboard = [[InlineKeyboardButton(p[0], callback_data=f"plan_{p[1]}")] for p in plans]
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="go_locations")])

    await q.edit_message_text(f"💎 {title}\nحجم سرویس رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    plan = q.data.split("_")[1]

    user_data[user_id]["plan"] = plan

    price_map = {"1": 369, "2": 738, "3": 1107, "4": 1476, "5": 1845, "10": 3690}
    price = price_map[plan]

    await q.edit_message_text(f"""
📦 فاکتور نهایی

♾ حجم : {plan}GB
💵 قیمت : {price} تومان

💳 کارت:
{CARD}

📸 رسید ارسال کن
""")

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    order_info = user_data.get(user_id, {})

    loc = order_info.get("loc", "نامشخص")
    plan = order_info.get("plan", "نامشخص")

    price_map = {"1": 369, "2": 738, "3": 1107, "4": 1476, "5": 1845, "10": 3690}
    price = price_map.get(plan, "نامشخص")

    for admin in ADMIN_IDS:
        forwarded = await context.bot.forward_message(
            chat_id=admin,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

        info_msg = await context.bot.send_message(
            chat_id=admin,
            text=f"""🧾 سفارش جدید

👤 کاربر: {user_id}
🌍 لوکیشن: {loc}
📦 پلن: {plan}GB
💵 قیمت: {price} تومان

👆 به این پیام یا رسید ریپلای کن"""
        )

        # مهم: ذخیره هر دو پیام
        user_messages[forwarded.message_id] = user_id
        user_messages[info_msg.message_id] = user_id

    await update.message.reply_text("✅ سفارش ثبت شد")

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.message.from_user.id

    if not is_admin(admin_id):
        return

    if not update.message.reply_to_message:
        return

    replied_id = update.message.reply_to_message.message_id

    if replied_id not in user_messages:
        return

    target_user = user_messages[replied_id]
    msg = update.message.text

    # ارسال برای مشتری
    await context.bot.send_message(
        chat_id=target_user,
        text=f"📩 پاسخ ادمین:\n\n{msg}"
    )

    # لاگ داخل بات
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"""📡 لاگ پیام

👤 ادمین: {admin_id}
🎯 کاربر: {target_user}

💬 پیام:
{msg}"""
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("home", home))

app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(accept_rules, pattern="accept_rules"))

app.add_handler(CallbackQueryHandler(locations, pattern="go_locations"))
app.add_handler(CallbackQueryHandler(plans, pattern="loc_"))
app.add_handler(CallbackQueryHandler(order, pattern="plan_"))

app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receipt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))

app.run_polling()
