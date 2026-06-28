import os
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TELEGRAM_TOKEN")

ADMIN_ID = 6269793768

user_states = {}


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📈 Formation Trading", callback_data="formation")],
        [InlineKeyboardButton("🤝 Service personnel", callback_data="service")],
        [InlineKeyboardButton("💼 Opportunité commerciale", callback_data="business")],
        [InlineKeyboardButton("📞 Contacter directement MrTech237", callback_data="contact")]
    ]

    text = """
👋 Bienvenue chez MrTech237.

Je suis l'assistant automatique de MrTech237.

Merci de sélectionner le motif de votre prise de contact.
"""

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# BOUTONS
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "formation":

        user_states[user_id] = "formation"

        keyboard = [
            [InlineKeyboardButton("🔰 Débutant", callback_data="niveau_debutant")],
            [InlineKeyboardButton("📊 Intermédiaire", callback_data="niveau_intermediaire")],
            [InlineKeyboardButton("📈 Avancé", callback_data="niveau_avance")],
            [InlineKeyboardButton("💰 Déjà rentable", callback_data="niveau_rentable")]
        ]

        await query.edit_message_text(
            "Quel est votre niveau actuel en trading ?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("niveau_"):

        niveau = query.data.replace("niveau_", "")
        context.user_data["niveau"] = niveau

        keyboard = [
            [InlineKeyboardButton("Starter - 100$", callback_data="pack_starter")],
            [InlineKeyboardButton("Pro - 200$", callback_data="pack_pro")],
            [InlineKeyboardButton("Elite - 500$", callback_data="pack_elite")]
        ]

        await query.edit_message_text(
            "Quel pack souhaitez-vous recevoir ?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("pack_"):

        pack = query.data.replace("pack_", "")
        context.user_data["pack"] = pack

        avantages = {
            "starter": """
🔥 PACK STARTER - 100$

✔ Formation 2 semaines
✔ Bases du trading
✔ Gestion du risque
✔ Ebook offert
✔ Groupe privé 1 mois
""",

            "pro": """
🔥 PACK PRO - 200$

✔ Formation 1 mois
✔ Analyse technique avancée
✔ Ebook Premium
✔ Canal VIP 3 mois
✔ Suivi hebdomadaire
✔ Assistance privée
""",

            "elite": """
🔥 PACK ELITE - 500$

✔ Coaching personnalisé 3 mois
✔ Sessions individuelles
✔ Canal VIP Premium
✔ Suivi des trades
✔ Analyse de portefeuille
✔ Support prioritaire
✔ Stratégies avancées
"""
        }

        await query.edit_message_text(
            avantages[pack] +
            """

💳 Moyens de paiement acceptés :

• MTN Mobile Money
• Orange Money
• PayPal
• USDT
• Bitcoin
• Virement bancaire

Veuillez maintenant décrire vos objectifs en trading.
"""
        )

        user_states[user_id] = "objectif"

    elif query.data == "service":

        user_states[user_id] = "service"

        await query.edit_message_text(
            """
Merci de décrire votre demande personnelle.

Exemples :

• partenariat
• service informatique
• collaboration
• projet personnel
• assistance technique
"""
        )

    elif query.data == "business":

        user_states[user_id] = "business"

        await query.edit_message_text(
            """
Merci de décrire votre opportunité commerciale ou votre projet.
"""
        )

    elif query.data == "contact":

        user_states[user_id] = "contact"

        await query.edit_message_text(
            """
Veuillez rédiger votre message destiné à MrTech237.
"""
        )


# =========================
# RECEPTION DES MESSAGES
# =========================
async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    user_id = user.id
    text = update.message.text

    state = user_states.get(user_id, "general")

    admin_message = f"""
📩 Nouvelle demande

👤 Nom : {user.full_name}
🆔 ID : {user.id}
📌 Username : @{user.username}

📂 Catégorie : {state}

📝 Message :

{text}
"""

    if "niveau" in context.user_data:
        admin_message += f"\n📊 Niveau : {context.user_data['niveau']}"

    if "pack" in context.user_data:
        admin_message += f"\n🎓 Pack : {context.user_data['pack']}"

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message
    )

    await update.message.reply_text(
        """
✅ Votre demande a bien été transmise à MrTech237.

Vous recevrez une réponse dès que possible.

Si votre demande est urgente, MrTech237 pourra vous contacter directement.
"""
    )


# =========================
# REPONDRE VIA LE BOT
# =========================
async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])

        message = " ".join(context.args[1:])

        await context.bot.send_message(
            chat_id=user_id,
            text=f"""
📩 Message de MrTech237

{message}
"""
        )

        await update.message.reply_text("✅ Message envoyé.")

    except Exception:
        await update.message.reply_text(
            """
Utilisation :

/reply ID_UTILISATEUR votre message
"""
        )


# =========================
# MAIN
# =========================
async def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_command))

    app.add_handler(CallbackQueryHandler(button))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_message
        )
    )

    print("✅ MrTech237 Assistant démarré")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
