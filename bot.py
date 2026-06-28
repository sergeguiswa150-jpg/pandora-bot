import os
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError(
        "La variable d'environnement TELEGRAM_TOKEN est manquante."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "🔐 Problème de connexion",
                callback_data="connexion"
            )
        ],
        [
            InlineKeyboardButton(
                "📦 Suivi de commande",
                callback_data="commande"
            )
        ],
        [
            InlineKeyboardButton(
                "🛒 Aide à l'achat",
                callback_data="achat"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Contacter un conseiller",
                callback_data="conseiller"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Bienvenue sur le support Pandora.\n\n"
        "Choisissez une option ci-dessous :",
        reply_markup=reply_markup
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    messages = {
        "connexion":
            "🔐 Procédure de récupération :\n\n"
            "1️⃣ Vérifiez votre adresse email\n"
            "2️⃣ Cliquez sur 'Mot de passe oublié'\n"
            "3️⃣ Suivez les instructions reçues",

        "commande":
            "📦 Veuillez envoyer votre numéro de commande afin que nous puissions vérifier son statut.",

        "achat":
            "🛒 Étapes pour effectuer un achat :\n\n"
            "1️⃣ Choisissez votre produit\n"
            "2️⃣ Ajoutez-le au panier\n"
            "3️⃣ Validez votre commande",

        "conseiller":
            "📞 Votre demande a été enregistrée.\n"
            "Un conseiller vous contactera prochainement."
    }

    await query.edit_message_text(
        messages.get(
            query.data,
            "❌ Option inconnue."
        )
    )


async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button
        )
    )

    print("✅ Bot lancé avec succès")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
