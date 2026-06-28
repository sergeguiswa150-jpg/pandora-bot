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
        "Bienvenue chez Pandora 👋\n\nComment puis-je vous aider ?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    responses = {
        "connexion": (
            "🔐 Problème de connexion\n\n"
            "1. Vérifiez votre adresse email\n"
            "2. Cliquez sur 'Mot de passe oublié'\n"
            "3. Suivez les instructions reçues"
        ),
        "commande": (
            "📦 Veuillez envoyer votre numéro de commande "
            "afin que nous puissions vérifier son statut."
        ),
        "achat": (
            "🛒 Pour acheter un produit :\n\n"
            "1️⃣ Choisissez votre article\n"
            "2️⃣ Ajoutez-le au panier\n"
            "3️⃣ Validez votre commande"
        ),
        "conseiller": (
            "📞 Votre demande a été enregistrée.\n"
            "Un conseiller vous contactera prochainement."
        ),
    }

    await query.edit_message_text(
        responses.get(query.data, "Je n'ai pas compris votre demande.")
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot démarré avec succès...")
    app.run_polling()


if __name__ == "__main__":
    main()