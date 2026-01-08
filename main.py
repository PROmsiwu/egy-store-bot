import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ الإعدادات الأساسية ---
TOKEN = '8218894623:AAFUfkCRWwYJltp-zVb8oxdSMwCf98V-yVM'
OWNER_ID = 8056457663 
OWNER_LINK = "https://t.me/ahmed3893"

# قاعدة بيانات وهمية (تختفي عند إعادة تشغيل البوت في Pydroid، يفضل لاحقاً استخدام SQLite)
# تم وضع بيانات أولية لك
store_data = {
    "items": [
        {"name": "100 جوهرة فري فاير", "price": 50, "category": "جواهر"},
        {"name": "60 شدة ببجي", "price": 40, "category": "شدات"}
    ]
}

# حالات الإدخال (لحفظ ما يفعله الأونر)
current_action = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = []
    
    # عرض المنتجات للزبائن
    for item in store_data["items"]:
        keyboard.append([InlineKeyboardButton(f"🛒 {item['name']} - {item['price']}ج", callback_data=f"buy_{item['name']}")])
    
    keyboard.append([InlineKeyboardButton("👨‍💻 تواصل مع أحمد", url=OWNER_LINK)])
    
    if user_id == OWNER_ID:
        keyboard.append([InlineKeyboardButton("⚙️ لوحة التحكم (أحمد)", callback_data='admin_main')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = "🚀 **متجر EGY STORE**\nاختر ما تريد شحنه 👇"
    
    if update.message:
        await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(msg, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == 'admin_main':
        keyboard = [
            [InlineKeyboardButton("➕ إضافة منتج جديد", callback_data='admin_add')],
            [InlineKeyboardButton("❌ حذف كل المنتجات", callback_data='admin_clear')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]
        ]
        await query.edit_message_text("🛠 **غرفة التحكم يا أحمد:**\nإضغط لإضافة منتج جديد وسيطلب منك البوت التفاصيل.", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == 'admin_add':
        current_action[OWNER_ID] = "waiting_for_name"
        await query.edit_message_text("📝 أرسل الآن **اسم المنتج** (مثال: 500 جوهرة):")

    elif query.data == 'admin_clear':
        store_data["items"] = []
        await query.edit_message_text("✅ تم مسح جميع المنتجات.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data='admin_main')]]))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID or OWNER_ID not in current_action:
        return

    action = current_action[OWNER_ID]
    
    if action == "waiting_for_name":
        current_action["temp_name"] = update.message.text
        current_action[OWNER_ID] = "waiting_for_price"
        await update.message.reply_text(f"تمام.. السعر كام لـ ({update.message.text})؟ (أرسل رقم فقط)")
    
    elif action == "waiting_for_price":
        try:
            price = int(update.message.text)
            name = current_action["temp_name"]
            store_data["items"].append({"name": name, "price": price})
            del current_action[OWNER_ID]
            await update.message.reply_text(f"✅ تم إضافة {name} بسعر {price}ج بنجاح!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة للقائمة", callback_data='main_menu')]]))
        except:
            await update.message.reply_text("❌ خطأ! أرسل رقم فقط للسعر.")

async def handle_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_name = query.data.replace('buy_', '')
    await query.edit_message_text(f"✅ تم اختيار: {item_name}\nتواصل مع أحمد للدفع: {OWNER_LINK}")
    
    # إشعار للأونر
    await context.bot.send_message(chat_id=OWNER_ID, text=f"🚨 **طلب جديد!**\nالعميل: {query.from_user.first_name}\nالمنتج: {item_name}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_admin, pattern='^admin_'))
    app.add_handler(CallbackQueryHandler(start, pattern='main_menu'))
    app.add_handler(CallbackQueryHandler(handle_buy, pattern='^buy_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    print("🚀 البوت شغال.. ضيف منتجاتك من التلجرام الآن!")
    app.run_polling()
