from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8653861753:AAEUuafpUZhmx_INOqR1oDdRgmtohkBaiZo"
ADMIN_ID = 5231145229

CHANNEL_USERNAME = "@Vortexsshop"
CHANNEL_LINK = "https://t.me/Vortexsshop"

CARD = "6219-8618-0647-8813"

user_data = {}

# 🔍 چک عضویت واقعی
async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🏠 منوی اصلی
async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 شروع خرید", callback_data="go_locations")]
    ]

    if update.message:
        await update.message.reply_text(
            "🏠 به Vortex Shop خوش آمدی",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.callback_query.edit_message_text(
            "🏠 به Vortex Shop خوش آمدی",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not await is_member(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join")]
        ]

        await update.message.reply_text(
            "⚠️ برای استفاده از ربات باید عضو کانال باشی:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await home(update, context)

# بررسی عضویت
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id

    if await is_member(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("🚀 شروع خرید", callback_data="go_locations")]
        ]

        await q.edit_message_text(
            "✅ عضویت تایید شد\nحالا وارد فروشگاه شو 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await q.answer("❌ هنوز عضو کانال نشدی", show_alert=True)

# لوکیشن‌ها
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

# پلن‌ها
async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    loc = q.data.split("_")[1]
    user_data[q.from_user.id] = {"loc": loc}

    if loc == "de":
        title = "🇩🇪 آلمان"
    elif loc == "nl":
        title = "🇳🇱 هلند"
    else:
        title = "🇹🇷 ترکیه"

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

# فاکتور
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    plan = q.data.split("_")[1]

    user_data[user_id]["plan"] = plan

    price_map = {
        "1": 400,
        "2": 800,
        "3": 1200,
        "4": 1600,
        "5": 2000,
        "10": 4000
    }

    price = price_map[plan]

    text = f"""
📦 فاکتور نهایی 👇

🔘 لوکیشن : {user_data[user_id]['loc']}
♾ حجم : {plan}GB
👤 کاربر : 2
⏳ زمان : نامحدود

💵 قیمت : {price} تومان

💳 کارت:
{CARD}

📸 بعد از واریز، رسید ارسال کن
"""

    await q.edit_message_text(text)

# 📥 رسید
async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    text = f"""
📥 رسید جدید

👤 @{user.username}
🆔 {user.id}
"""

    await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    await update.message.forward(chat_id=ADMIN_ID)

    await update.message.reply_text("✅ رسید ارسال شد، منتظر تایید باش")

# اجرا
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("home", home))

app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(home, pattern="home"))
app.add_handler(CallbackQueryHandler(locations, pattern="go_locations"))
app.add_handler(CallbackQueryHandler(plans, pattern="loc_"))
app.add_handler(CallbackQueryHandler(order, pattern="plan_"))

app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receipt))

app.run_polling()
