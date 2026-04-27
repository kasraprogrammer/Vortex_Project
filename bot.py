from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# ⚠️ توکن خود را اینجا قرار دهید
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
    keyboard = [[InlineKeyboardButton("🚀 شروع خرید", callback_data="go_plans")]]
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

    keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]
    await update.message.reply_text(RULES_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))

# ================= CHECK JOIN =================

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    if await is_member(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]
        await q.edit_message_text(RULES_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await q.answer("❌ هنوز عضو کانال نشدی!", show_alert=True)

# ================= ACCEPT RULES =================

async def accept_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    keyboard = [[InlineKeyboardButton("🚀 شروع خرید", callback_data="go_plans")]]
    await q.edit_message_text(
        "✅ قوانین پذیرفته شد\n\nحالا میتونی خریدت رو شروع کنی 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= PLANS =================

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # قیمت هر گیگ 300 تومان
    base_price = 300
    plan_sizes = [1, 2, 3, 4, 5, 10]
    
    keyboard = []
    for p in plan_sizes:
        total_price = p * base_price
        keyboard.append([InlineKeyboardButton(f"📦 {p} گیگابایت - {total_price:,} تومان", callback_data=f"plan_{p}")])

    keyboard.append([InlineKeyboardButton("🔙 برگشت به خانه", callback_data="home")])

    await q.edit_message_text(
        "⚡️ سرویس پرسرعت اختصاصی Vortex\nحجم مورد نظر خود را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= ORDER =================

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    plan = int(q.data.split("_")[1])
    user_data[user_id] = {"plan": plan}

    price = plan * 300

    await q.edit_message_text(f"""
📦 فاکتور نهایی سفارش

✨ نوع سرویس: پرسرعت اختصاصی
♾ حجم انتخابی: {plan} گیگابایت
💵 مبلغ قابل پرداخت : {price:,} تومان

💳 شماره کارت جهت واریز:
`{CARD}`

📸 لطفا پس از واریز، تصویر رسید را در همینجا ارسال کنید تا سرویس شما فعال شود.
""", parse_mode="Markdown")

# ================= RECEIPT =================

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    order_info = user_data.get(user_id, {})

    plan = order_info.get("plan", 0)

    if plan == 0:
        await update.message.reply_text("❌ ابتدا یک پلن انتخاب کنید.")
        return

    price = int(plan) * 300

    for admin in ADMIN_IDS:
        # ارسال رسید برای ادمین
        sent = await context.bot.forward_message(
            chat_id=admin,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
        user_messages[sent.message_id] = user_id

        await context.bot.send_message(
            chat_id=admin,
            text=f"""
🧾 سفارش جدید رسید!

👤 کاربر: `{user_id}`
📦 پلن: {plan}GB پرسرعت
💵 قیمت واریزی: {price:,} تومان

👆 رسید بالا رو بررسی کن.
""", parse_mode="Markdown"
        )

    await update.message.reply_text("✅ رسید شما دریافت شد و برای مدیریت ارسال گردید. منتظر تایید بمانید.")

# ================= ADMIN REPLY =================

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.message.from_user.id

    if not is_admin(admin_id) or not update.message.reply_to_message:
        return

    replied_id = update.message.reply_to_message.message_id
    if replied_id not in user_messages:
        return

    target_user = user_messages[replied_id]
    msg_text = update.message.text

    try:
        await context.bot.send_message(chat_id=target_user, text=f"📩 پاسخ ادمین:\n\n{msg_text}")
        if admin_id != OWNER_ID:
            log_text = f"📝 **لاگ پیام ادمین**\n\n👤 ادمین: `{admin_id}`\n🎯 به کاربر: `{target_user}`\n💬 متن:\n{msg_text}"
            await context.bot.send_message(chat_id=OWNER_ID, text=log_text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال: {e}")

# ================= RUN =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("home", home))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(accept_rules, pattern="accept_rules"))
app.add_handler(CallbackQueryHandler(plans, pattern="go_plans"))
app.add_handler(CallbackQueryHandler(order, pattern="plan_"))
app.add_handler(CallbackQueryHandler(home, pattern="home"))

app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receipt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))

app.run_polling()
