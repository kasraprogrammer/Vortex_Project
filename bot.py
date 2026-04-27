import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# ⚠️ تنظیمات اصلی
TOKEN = "8653861753:AAEUuafpUZhmx_INOqR1oDdRgmtohkBaiZo"
ADMIN_IDS = [5231145229, 6225624558]
OWNER_ID = 5231145229
CHANNEL_USERNAME = "@Vortexsshop"
CHANNEL_LINK = "https://t.me/Vortexsshop"
CARD = "6219-8618-0647-8813"

user_data = {}
user_messages = {}
DIVIDER = "━━━━━━━━━━━━━━"

# ================= DATABASE =================

def init_db():
    conn = sqlite3.connect('vortex_shop.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('vortex_shop.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('vortex_shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

init_db()

# ================= FUNCTIONS =================

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# متن جدید قوانین شما
RULES_TEXT = f"""
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

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    add_user(user_id)
    
    if not await is_member(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join")]]
        await update.message.reply_text(f"<b>⚠️ برای استفاده باید عضو کانال باشی:</b>\n\n{DIVIDER}",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]
    await update.message.reply_text(RULES_TEXT, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if await is_member(context.bot, q.from_user.id):
        await q.answer("✅ عضویت تایید شد!")
        keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]
        await q.edit_message_text(RULES_TEXT, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    else:
        await q.answer("❌ هنوز عضو کانال نشدی!", show_alert=True)

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 شروع خرید", callback_data="go_plans")],
        [InlineKeyboardButton("👨‍💻 پشتیبانی", url="https://t.me/VortexShop_Support"), InlineKeyboardButton("📢 کانال ما", url=CHANNEL_LINK)]
    ]
    text = f"<b>🏠 به Vortex Shop خوش آمدی</b>\n\n{DIVIDER}\nلطفاً برای ادامه انتخاب کنید:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    keyboard = [
        [InlineKeyboardButton("📦 1GB | 300T", callback_data="plan_1"), InlineKeyboardButton("📦 2GB | 600T", callback_data="plan_2")],
        [InlineKeyboardButton("📦 3GB | 900T", callback_data="plan_3"), InlineKeyboardButton("📦 4GB | 1,200T", callback_data="plan_4")],
        [InlineKeyboardButton("📦 5GB | 1,500T", callback_data="plan_5"), InlineKeyboardButton("📦 10GB | 3,000T", callback_data="plan_10")],
        [InlineKeyboardButton("🔙 برگشت به خانه", callback_data="home")]
    ]
    await q.edit_message_text(f"<b>⚡️ سرویس Vortex</b>\n{DIVIDER}\nحجم انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    plan = int(q.data.split("_")[1])
    user_data[q.from_user.id] = {"plan": plan}
    await q.edit_message_text(f"<b>📦 فاکتور نهایی</b>\n{DIVIDER}\nحجم: {plan}GB\nقیمت: {plan*300:,}T\n\n💳 کارت: <code>{CARD}</code>\n\n📸 رسید را اینجا بفرستید.", parse_mode="HTML")

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if is_admin(user_id): return
    plan = user_data.get(user_id, {}).get("plan", 0)
    if plan == 0: return

    for admin in ADMIN_IDS:
        try:
            sent = await context.bot.forward_message(chat_id=admin, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
            user_messages[sent.message_id] = user_id
            await context.bot.send_message(chat_id=admin, text=f"🧾 جدید: {user_id}\n📦 {plan}GB\n⚠️ ریپلای روی عکس برای پاسخ.", parse_mode="HTML")
        except: continue
    await update.message.reply_text("✅ رسید دریافت شد.")

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.message.from_user.id
    if not is_admin(admin_id) or not update.message.reply_to_message: return
    
    replied_id = update.message.reply_to_message.message_id
    if replied_id in user_messages:
        target_user = user_messages[replied_id]
        msg_text = update.message.text
        try:
            await context.bot.send_message(chat_id=target_user, text=f"<b>📩 پاسخ پشتیبانی:</b>\n\n{msg_text}", parse_mode="HTML")
            # گزارش به شما (Owner)
            if admin_id != OWNER_ID:
                await context.bot.send_message(chat_id=OWNER_ID, text=f"👮‍♂️ گزارش ادمین {admin_id} به {target_user}:\n{msg_text}")
            await update.message.reply_text("✅ ارسال شد.")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا: {e}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    if not context.args:
        await update.message.reply_text("❌ بنویس: /send متن پیام")
        return
    text = " ".join(context.args)
    users = get_all_users()
    done, fail = 0, 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>اطلاعیه فروشگاه</b>\n\n{text}", parse_mode="HTML")
            done += 1
        except: fail += 1
    await update.message.reply_text(f"✅ پایان ارسال.\nموفق: {done}\nناموفق: {fail}")

# ================= RUN =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("send", broadcast))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(home, pattern="accept_rules|home"))
app.add_handler(CallbackQueryHandler(plans, pattern="go_plans"))
app.add_handler(CallbackQueryHandler(order, pattern="plan_"))
app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receipt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))

print("Vortex Shop is running...")
app.run_polling()
