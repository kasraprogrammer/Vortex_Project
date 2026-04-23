from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# ⚠️ توکن رو خودت بذار
TOKEN = "8653861753:AAEUuafpUZhmx_INOqR1oDdRgmtohkBaiZo"

ADMIN_IDS = [5231145229, 6225624558]
OWNER_ID = 5231145229

CHANNEL_USERNAME = "@Vortexsshop"
CHANNEL_LINK = "https://t.me/Vortexsshop"

CARD = "6219-8618-0647-8813"

user_data = {}
user_messages = {}

# ================= RULES =================

RULES_TEXT = """
📜 قوانین و مقررات استفاده از سرویس
━━━━━━━━━━━━━━━━━━━━━━

۱ — استفاده از سرویس‌ها صرفاً برای مصرف شخصی می‌باشد و در صورت قرار دادن به عنوان اوتباند یا پخش کردن در کانال‌های مختلف، بدون اخطار کل اکانت بن خواهد شد و هزینه‌ای عودت داده نمی‌شود. ⚠️🚫

۲ — به علت شرایط بسیار سخت در برقراری ارتباط با خارج از کشور، هیچ‌کدام از سرویس‌ها دارای تضمین نمی‌باشد. 🌍❌

۳ — قیمت‌ها به صورت منصفانه به نسبت زمان و هزینه‌هایی که برای برقراری اتصال انجام می‌شود، تعیین شده است. 💰⚖️

۴ — سرویس به صورت خیلی محدود ارائه می‌شود و امکان ارائه یوزر تست نیست. 🔒🙅‍♂️

۵ — 📡 فیلترهای ما روی شبکه اینترنشنال بسته است 🔴

بیشتر مشتریان ما برای کارهای درسی، پروژه‌های دانشجویی و ارتباط با خانواده از سرویس استفاده می‌کنند 💙

━━━━━━━━━━━━━━━━━━━━━━
با زدن دکمه "✅ می‌پذیرم" تأیید می‌کنی که قوانین را خوانده‌ای.
"""

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

    # بعد از عضویت → مستقیم قوانین
    keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]

    await update.message.reply_text(
        RULES_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= CHECK JOIN =================

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id

    if await is_member(context.bot, user_id):

        keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]

        await q.edit_message_text(
            RULES_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await q.answer("❌ هنوز عضو کانال نشدی!", show_alert=True)

# ================= ACCEPT RULES =================

async def accept_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    keyboard = [[InlineKeyboardButton("🚀 شروع خرید", callback_data="go_locations")]]

    await q.edit_message_text(
        "✅ قوانین پذیرفته شد\n\nحالا میتونی خریدت رو شروع کنی 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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

    await q.edit_message_text(
        "💎 لوکیشن سرویس رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= PLANS =================

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

# ================= RECEIPT =================

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    order_info = user_data.get(user_id, {})

    loc = order_info.get("loc", "نامشخص")
    plan = order_info.get("plan", "نامشخص")

    price_map = {"1": 369, "2": 738, "3": 1107, "4": 1476, "5": 1845, "10": 3690}
    price = price_map.get(plan, "نامشخص")

    for admin in ADMIN_IDS:
        sent = await context.bot.forward_message(
            chat_id=admin,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

        user_messages[sent.message_id] = user_id

        await context.bot.send_message(
            chat_id=admin,
            text=f"""
🧾 سفارش جدید

👤 کاربر: {user_id}
🌍 لوکیشن: {loc}
📦 پلن: {plan}GB
💵 قیمت: {price} تومان

👆 رسید بالا فوروارد شد
"""
        )

    await update.message.reply_text("✅ سفارش ثبت شد")

# ================= ADMIN REPLY =================

# ================= ADMIN REPLY =================

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_user = update.message.from_user
    admin_id = admin_user.id

    # فقط ادمین‌ها بتونن ریپلای کنن
    if not is_admin(admin_id):
        return

    # بررسی اینکه آیا روی پیامی ریپلای شده یا نه
    if not update.message.reply_to_message:
        return

    replied_id = update.message.reply_to_message.message_id

    # پیدا کردن یوزر آیدی مشتری از دیکشنری پیام‌ها
    if replied_id not in user_messages:
        return

    target_user = user_messages[replied_id]
    msg_text = update.message.text

    try:
        # ۱. ارسال پیام برای مشتری
        await context.bot.send_message(
            chat_id=target_user,
            text=f"📩 پاسخ ادمین:\n\n{msg_text}"
        )
        
        # ۲. ارسال لاگ برای مالک (Owner)
        # اگر خودِ مالک جواب داده بود، نیازی نیست دوباره برای خودش لاگ بره
        if admin_id != OWNER_ID:
            log_text = (
                f"📝 **لاگ پیام ادمین**\n\n"
                f"👤 ادمین: `{admin_id}`\n"
                f"🎯 به کاربر: `{target_user}`\n"
                f"💬 متن پیام:\n{msg_text}"
            )
            await context.bot.send_message(chat_id=OWNER_ID, text=log_text, parse_mode="Markdown")
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال پیام: {e}")

# ================= RUN =================

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
