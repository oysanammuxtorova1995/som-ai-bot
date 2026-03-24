import os
import logging
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# 1. Yashirin sozlamalarni yuklash
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")

# Logging (Xatolarni terminalda ko'rish uchun)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# 2. Mahsulotlar ro'yxati
PRODUCTS = {
    "1": {
        "name": "Ayollar ko'ylagi",
        "price": "180 000 so'm",
        "description": "Nafis va qulay kundalik ko'ylak",
    },
    "2": {
        "name": "Erkaklar futbolkasi",
        "price": "95 000 so'm",
        "description": "Yengil va qulay futbolka",
    },
    "3": {
        "name": "Bolalar kostyumi",
        "price": "150 000 so'm",
        "description": "Bayram va tadbirlar uchun chiroyli kostyum",
    },
}

# Buyurtma bosqichlari
SELECT_PRODUCT, ENTER_ADDRESS, ENTER_PHONE = range(3)

# --- KLAVIATURA ---
def main_menu():
    keyboard = [
        ["🛍 Mahsulotlar", "💰 Narxlar"],
        ["📦 Buyurtma berish", "👨‍💼 Operator"],
        ["ℹ️ Biz haqimizda"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- ASOSIY FUNKSIYALAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! So'm AI botiga xush kelibsiz.\nBo'limni tanlang:",
        reply_markup=main_menu()
    )

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🛍 **Mahsulotlarimiz:**\n\n"
    for p_id, p in PRODUCTS.items():
        text += f"**{p_id}. {p['name']}**\nNarxi: {p['price']}\n{p['description']}\n\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def show_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💰 **Narxlar ro'yxati:**\n\n"
    for p in PRODUCTS.values():
        text += f"• {p['name']}: {p['price']}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# --- BUYURTMA BERISH (CONVERSATION) ---
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📦 Mahsulot raqamini yuboring:\n\n"
    for p_id, p in PRODUCTS.items():
        text += f"{p_id}. {p['name']} - {p['price']}\n"
    await update.message.reply_text(text)
    return SELECT_PRODUCT

async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p_id = update.message.text.strip()
    if p_id not in PRODUCTS:
        await update.message.reply_text("❌ Xato raqam. Qayta urinib ko'ring.")
        return SELECT_PRODUCT
    
    context.user_data["product_id"] = p_id
    await update.message.reply_text(f"✅ Tanlandi: {PRODUCTS[p_id]['name']}\n📍 Manzilingizni yozing:")
    return ENTER_ADDRESS

async def enter_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text.strip()
    await update.message.reply_text("📞 Telefon raqamingizni yuboring:")
    return ENTER_PHONE

async def enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text.strip()
    product = PRODUCTS[context.user_data["product_id"]]
    user = update.effective_user

    # Admin uchun hisobot
    report = (
        "🔔 **Yangi buyurtma!**\n\n"
        f"👤 Mijoz: {user.full_name}\n"
        f"📦 Mahsulot: {product['name']}\n"
        f"📍 Manzil: {context.user_data['address']}\n"
        f"📞 Tel: {context.user_data['phone']}"
    )

    # Adminga yuborish (Guruhga)
    if ADMIN_GROUP_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=report, parse_mode="Markdown")
        except:
            pass

    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi!", reply_markup=main_menu())
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Buyurtma bekor qilindi.", reply_markup=main_menu())
    return ConversationHandler.END

# --- ISHGA TUSHIRISH ---
def main():
    app = Application.builder().token(TOKEN).build()

    order_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📦 Buyurtma berish$"), start_order)],
        states={
            SELECT_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_product)],
            ENTER_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_address)],
            ENTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(order_handler)
    app.add_handler(MessageHandler(filters.Regex("^🛍 Mahsulotlar$"), show_products))
    app.add_handler(MessageHandler(filters.Regex("^💰 Narxlar$"), show_prices))
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ Biz haqimizda$"), lambda u, c: u.message.reply_text("So'm AI — Sifatli savdo boti.")))
    app.add_handler(MessageHandler(filters.Regex("^👨‍💼 Operator$"), lambda u, c: u.message.reply_text("👨‍💼 Bog'lanish: @admin_username")))

    print("🚀 Bot ishlamoqda...")
    app.run_polling()

if __name__ == "__main__":
    main()
