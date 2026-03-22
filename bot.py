from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# =========================
# BOT TOKEN
# BotFather bergan tokenni shu yerga qo'ying
# =========================
TOKEN = "8605383684:AAFSvy2St2NEvecjVfB5M3G1iBPucSulPM4"

# =========================
# MAHSULOTLAR
# Hozircha oddiy ro'yxat
# Keyin database ga o'tkazamiz
# =========================
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

# =========================
# BUYURTMA HOLATLARI
# =========================
SELECT_PRODUCT, ENTER_ADDRESS, ENTER_PHONE = range(3)


def main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        ["🛍 Mahsulotlar", "💰 Narxlar"],
        ["📦 Buyurtma berish", "👨‍💼 Operator"],
        ["ℹ️ Biz haqimizda"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Assalomu alaykum!\n\n"
        "So'm AI botiga xush kelibsiz.\n"
        "Quyidagi bo'limlardan birini tanlang."
    )
    await update.message.reply_text(text, reply_markup=main_menu())


async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "🛍 Mahsulotlar ro'yxati:\n\n"

    for product_id, product in PRODUCTS.items():
        text += (
            f"{product_id}. {product['name']}\n"
            f"Narxi: {product['price']}\n"
            f"Tavsif: {product['description']}\n\n"
        )

    await update.message.reply_text(text, reply_markup=main_menu())


async def show_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "💰 Narxlar:\n\n"

    for product in PRODUCTS.values():
        text += f"- {product['name']}: {product['price']}\n"

    await update.message.reply_text(text, reply_markup=main_menu())


async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "ℹ️ So'm AI — mahsulotlarni ko'rsatish, "
        "buyurtma olish va savdoni yengillashtirish uchun yaratilgan bot."
    )
    await update.message.reply_text(text, reply_markup=main_menu())


async def contact_operator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👨‍💼 Operator tez orada siz bilan bog'lanadi.",
        reply_markup=main_menu(),
    )


# =========================
# BUYURTMA BOSHLASH
# =========================
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = "📦 Buyurtma uchun mahsulot raqamini yuboring:\n\n"

    for product_id, product in PRODUCTS.items():
        text += f"{product_id}. {product['name']} - {product['price']}\n"

    await update.message.reply_text(text)
    return SELECT_PRODUCT


async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    product_id = update.message.text.strip()

    if product_id not in PRODUCTS:
        await update.message.reply_text("Noto'g'ri mahsulot raqami. Qayta yuboring.")
        return SELECT_PRODUCT

    context.user_data["product_id"] = product_id
    product = PRODUCTS[product_id]

    await update.message.reply_text(
        f"Siz tanladingiz: {product['name']}\n\n"
        "Endi manzilingizni yozing:"
    )
    return ENTER_ADDRESS


async def enter_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["address"] = update.message.text.strip()
    await update.message.reply_text("Telefon raqamingizni yozing:")
    return ENTER_PHONE


async def enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["phone"] = update.message.text.strip()
    product = PRODUCTS[context.user_data["product_id"]]

    order_text = (
        "✅ Buyurtmangiz qabul qilindi!\n\n"
        f"Mahsulot: {product['name']}\n"
        f"Narx: {product['price']}\n"
        f"Manzil: {context.user_data['address']}\n"
        f"Telefon: {context.user_data['phone']}\n\n"
        "Tez orada siz bilan bog'lanamiz."
    )

    await update.message.reply_text(order_text, reply_markup=main_menu())
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Buyurtma bekor qilindi.",
        reply_markup=main_menu(),
    )
    return ConversationHandler.END


# =========================
# MENYU BOSHQARUVI
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == "🛍 Mahsulotlar":
        await show_products(update, context)
    elif text == "💰 Narxlar":
        await show_prices(update, context)
    elif text == "👨‍💼 Operator":
        await contact_operator(update, context)
    elif text == "ℹ️ Biz haqimizda":
        await about_us(update, context)
    else:
        await update.message.reply_text(
            "Iltimos, menyudagi tugmalardan foydalaning.",
            reply_markup=main_menu(),
        )


def main() -> None:
    app = Application.builder().token(TOKEN).build()

    order_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📦 Buyurtma berish$"), start_order)
        ],
        states={
            SELECT_PRODUCT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_product)
            ],
            ENTER_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_address)
            ],
            ENTER_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_phone)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_order)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(order_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
