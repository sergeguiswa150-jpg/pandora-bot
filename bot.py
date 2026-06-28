import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Problème de connexion", callback_data="connexion")],
        [InlineKeyboardButton("📦 Suivi de commande", callback_data="commande")],
        [InlineKeyboardButton("🛒 Aide à l'achat", callback_data="achat")],
        [InlineKeyboardButton("📞 Contacter un conseiller", callback_data="conseiller")],
    ]

    await update.message.reply_text(
        "Bienvenue sur le support Pandora 👋",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    messages = {
        "connexion": "Essayez la réinitialisation du mot de passe.",
        "commande": "Veuillez envoyer votre numéro de commande.",
        "achat": "Choisissez un produit puis ajoutez-le au panier.",
        "conseiller": "Un conseiller vous contactera bientôt.",
    }

    await query.edit_message_text(messages.get(query.data, "Option inconnue"))


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot lancé avec succès")
    app.run_polling()


if __name__ == "__main__":
    main()
