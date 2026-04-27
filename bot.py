from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# ⚠️ تنظیمات توکن و شناسه‌ها
TOKEN = "8653861753:AAEUuafpUZhmx_INOqR1oDdRgmtohkBaiZo"
ADMIN_IDS = [5231145229, 6225624558]
OWNER_ID = 5231145229
CHANNEL_USERNAME = "@Vortexsshop"
CHANNEL_LINK = "https://t.me/Vortexsshop"
CARD = "6219-8618-0647-8813"

# دیتابیس‌های موقت (در صورت ری‌استارت پاک می‌شوند)
user_data = {}
user_messages = {}

# جداکننده گرافیکی برای متن‌ها
DIVIDER = "━━━━━━━━━━━━━━"

# ================= FUNCTIONS =================

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # چک کردن عضویت در کانال
    if not await is_member(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join")]
        ]
        await update.message.reply_text(
            f"<b>⚠️ برای استفاده باید عضو کانال باشی:</b>\n\nلطفاً ابتدا در کانال ما عضو شده و سپس دکمه بررسی را بزنید.\n\n{DIVIDER}",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML"
        )
        return

    # نمایش متن کامل قوانین طبق درخواست شما
    rules_text = f"""
<b>📜 قوانین و مقررات استفاده از سرویس</b>
{DIVIDER}

۱ — استفاده از سرویس‌ها صرفاً برای <b>مصرف شخصی</b> می‌باشد و در صورت قرار دادن به عنوان اوتباند یا پخش کردن در کانال‌های مختلف، بدون اخطار کل اکانت <b>بن</b> خواهد شد و هزینه‌ای عودت داده نمی‌شود. ⚠️🚫

۲ — به علت شرایط بسیار سخت در برقراری ارتباط با خارج از کشور، هیچ‌کدام از سرویس‌ها دارای <b>تضمین</b> نمی‌باشد. 🌍❌

۳ — قیمت‌ها به صورت منصفانه به نسبت زمان و هزینه‌هایی که برای برقراری اتصال انجام می‌شود، تعیین شده است. 💰⚖️

۴ — سرویس به صورت خیلی محدود ارائه می‌شود و امکان ارائه <b>یوزر تست</b> نیست. 🔒🙅‍♂️

۵ — 📡 <b>فیلترهای ما روی شبکه اینترنشنال بسته است</b> 🔴

بیشتر مشتریان ما برای کارهای درسی، پروژه‌های دانشجویی و ارتباط با خانواده از سرویس استفاده می‌کنند 💙

{DIVIDER}
با زدن دکمه <b>"✅ می‌پذیرم"</b> تأیید می‌کنی که قوانین را خوانده‌ای.
"""
    keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]
    await update.message.reply_text(rules_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if await is_member(context.bot, q.from_user.id):
        await q.answer("✅ خوش آمدید!")
        # بعد از تایید عضویت، قوانین نمایش داده شود
        await start(update, context)
    else:
        await q.answer("❌ هنوز عضو کانال نشدی!", show_alert=True)

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 شروع خرید", callback_data="go_plans")],
        [InlineKeyboardButton("👨‍💻 پشتیبانی", url="https://t.me/VortexShop_Support"), InlineKeyboardButton("📢 کانال ما", url=CHANNEL_LINK)]
    ]
    text = f"<b>🏠 به Vortex Shop خوش آمدی</b>\n\n{DIVIDER}\nلطفاً برای ادامه انتخاب کنید:"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    # چیدمان دکمه‌ها به صورت جفتی
    keyboard = [
        [InlineKeyboardButton("📦 1GB | 300T", callback_data="plan_1"), InlineKeyboardButton("📦 2GB | 600T", callback_data="plan_2")],
        [InlineKeyboardButton("📦 3GB | 900T", callback_data="plan_3"), InlineKeyboardButton("📦 4GB | 1,200T", callback_data="plan_4")],
        [InlineKeyboardButton("📦 5GB | 1,500T", callback_data="plan_5"), InlineKeyboardButton("📦 10GB | 3,000T", callback_data="plan_10")],
        [InlineKeyboardButton("🔙 برگشت به خانه", callback_data="home")]
    ]
    
    await q.edit_message_text(
        f"<b>⚡️ سرویس پرسرعت اختصاصی Vortex</b>\n{DIVIDER}\nحجم مورد نظر خود را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML"
    )

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user_id = q.from_user.id
    plan = int(q.data.split("_")[1])
    user_data[user_id] = {"plan": plan}
    price = plan * 300

    await q.edit_message_text(f"""
<b>📦 فاکتور نهایی سفارش</b>
{DIVIDER}
✨ نوع سرویس: <code>Vortex Private</code>
♾ حجم انتخابی: <code>{plan} گیگابایت</code>
💵 مبلغ قابل پرداخت: <b>{price:,} تومان</b>

💳 شماره کارت جهت واریز:
<code>{CARD}</code>

{DIVIDER}
📸 <b>لطفاً پس از واریز، تصویر رسید را در همینجا ارسال کنید.</b>
""", parse_mode="HTML")

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    order_info = user_data.get(user_id, {})
    plan = order_info.get("plan", 0)

    if plan == 0:
        await update.message.reply_text("❌ ابتدا یک پلن انتخاب کنید.")
        return

    price = plan * 300
    for admin in ADMIN_IDS:
        # فوروارد عکس رسید
        sent = await context.bot.forward_message(chat_id=admin, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
        user_messages[sent.message_id] = user_id
        
        # اطلاع‌رسانی به ادمین
        await context.bot.send_message(
            chat_id=admin,
            text=f"<b>🧾 سفارش جدید رسید!</b>\n\n👤 کاربر: <code>{user_id}</code>\n📦 پلن: {plan}GB\n💵 قیمت: {price:,}T\n\n👆 رسید بالا رو چک کن.",
            parse_mode="HTML"
        )

    await update.message.reply_text("✅ <b>رسید شما دریافت شد.</b>\n\nمنتظر تایید مدیریت بمانید.", parse_mode="HTML")

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
        await context.bot.send_message(chat_id=target_user, text=f"<b>📩 پاسخ پشتیبانی:</b>\n\n{msg_text}", parse_mode="HTML")
        await update.message.reply_text("✅ پیام به کاربر ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال: {e}")

# ================= RUN =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("home", home))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(home, pattern="accept_rules")) # بعد از پذیرش قوانین میره به هوم
app.add_handler(CallbackQueryHandler(plans, pattern="go_plans"))
app.add_handler(CallbackQueryHandler(order, pattern="plan_"))
app.add_handler(CallbackQueryHandler(home, pattern="home"))

app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receipt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))

print("Vortex Shop Bot is now Live!")
app.run_polling()
