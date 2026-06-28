import asyncio
import logging
import os
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
    ConversationHandler,
    filters
)

from config import (
    TOKEN,
    ADMIN_ID,
    BOT_NAME,
    PAYMENT_METHODS
)

from payments import PACKS

from database import (
    add_prospect,
    get_prospects,
    update_status
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

LEVEL = 1
PACK = 2
CAPITAL = 3
OBJECTIVE = 4
SERVICE = 5

relay_sessions = {}

user_data_storage = {}


def get_port():
    try:
        return int(os.getenv("PORT", "8443"))
    except ValueError:
        return 8443


def get_webhook_url():
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        return webhook_url.rstrip("/") + f"/{TOKEN}"

    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        return render_url.rstrip("/") + f"/{TOKEN}"

    return None


def calculate_score(pack, capital):

    score = 0

    if pack == "starter":
        score += 1

    elif pack == "pro":
        score += 3

    elif pack == "elite":
        score += 5

    if capital == "<100":
        score += 1

    elif capital == "100-500":
        score += 2

    elif capital == "500-2000":
        score += 4

    elif capital == ">2000":
        score += 6

    return score
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "📈 Formation Trading",
                callback_data="formation"
            )
        ],

        [
            InlineKeyboardButton(
                "🤝 Service personnel",
                callback_data="service"
            )
        ],

        [
            InlineKeyboardButton(
                "💼 Opportunité commerciale",
                callback_data="business"
            )
        ],

        [
            InlineKeyboardButton(
                "📞 Contacter directement MrTech237",
                callback_data="contact"
            )
        ]
    ]

    await update.message.reply_text(
        f"""
👋 Bienvenue chez {BOT_NAME}

Je suis l'assistant automatique de MrTech237.

Veuillez choisir le motif de votre prise de contact.
""",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )
async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    data = query.data

    if not data:
        return

    if data == "formation":

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔰 Débutant",
                    callback_data="level_beginner"
                )
            ],

            [
                InlineKeyboardButton(
                    "📊 Intermédiaire",
                    callback_data="level_intermediate"
                )
            ],

            [
                InlineKeyboardButton(
                    "📈 Avancé",
                    callback_data="level_advanced"
                )
            ],

            [
                InlineKeyboardButton(
                    "💰 Déjà rentable",
                    callback_data="level_profitable"
                )
            ]
        ]

        await query.edit_message_text(
            """
📈 FORMATION TRADING

Quel est votre niveau actuel en trading ?
""",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return

    if data.startswith("level_"):

        level = data.replace(
            "level_",
            ""
        )

        user_data_storage[user_id] = {
            "level": level
        }

        keyboard = [
            [
                InlineKeyboardButton(
                    "Starter - 100$",
                    callback_data="pack_starter"
                )
            ],

            [
                InlineKeyboardButton(
                    "Pro - 200$",
                    callback_data="pack_pro"
                )
            ],

            [
                InlineKeyboardButton(
                    "Elite - 500$",
                    callback_data="pack_elite"
                )
            ]
        ]

        await query.edit_message_text(
            """
Choisissez le programme qui vous intéresse :
""",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return

    if data.startswith("pack_"):

        pack = data.replace(
            "pack_",
            ""
        )

        user_data_storage[user_id]["pack"] = pack

        keyboard = [
            [
                InlineKeyboardButton(
                    "<100$",
                    callback_data="capital_<100"
                )
            ],

            [
                InlineKeyboardButton(
                    "100$ - 500$",
                    callback_data="capital_100-500"
                )
            ],

            [
                InlineKeyboardButton(
                    "500$ - 2000$",
                    callback_data="capital_500-2000"
                )
            ],

            [
                InlineKeyboardButton(
                    ">2000$",
                    callback_data="capital_>2000"
                )
            ]
        ]

        await query.edit_message_text(
            f"""
🎓 Pack sélectionné : {pack.upper()}

💵 Prix : {PACKS[pack]['price']}

{PACKS[pack]['advantages']}

Quel est votre capital actuel ?
""",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return
    if data.startswith("capital_"):

        capital = data.replace(
            "capital_",
            ""
        )

        user_data_storage[user_id]["capital"] = capital

        await query.edit_message_text(
            """
🎯 Décris maintenant :

• ton objectif en trading
• ce que tu souhaites apprendre
• tes attentes concernant la formation

Écris simplement ton message ci-dessous.
"""
        )

        context.user_data["waiting_objective"] = True

        return

    if data == "service":

        context.user_data["service_request"] = True

        await query.edit_message_text(
            """
🤝 SERVICE PERSONNEL

Merci de décrire précisément votre demande.
Votre message sera transmis directement à MrTech237.
"""
        )

        return

    if data == "business":

        context.user_data["business_request"] = True

        await query.edit_message_text(
            """
💼 OPPORTUNITÉ COMMERCIALE

Merci de présenter votre projet ou votre proposition.
Votre message sera transmis à MrTech237.
"""
        )

        return

    if data == "contact":

        context.user_data["direct_contact"] = True

        await query.edit_message_text(
            """
📞 CONTACT DIRECT

Merci de rédiger votre message destiné à MrTech237.
"""
        )

        return
async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user
    user_id = user.id

    if not update.message or not update.message.text:
        return

    message = update.message.text.strip()

    if not message:
        return

    if context.user_data.get(
        "waiting_objective"
    ):
        if user_id not in user_data_storage:
            await update.message.reply_text(
                "La conversation a été réinitialisée. Veuillez relancer /start."
            )
            context.user_data.clear()
            return

        level = user_data_storage[user_id]["level"]

        pack = user_data_storage[user_id]["pack"]

        capital = user_data_storage[user_id]["capital"]

        score = calculate_score(
            pack,
            capital
        )

        add_prospect(
            telegram_id=user_id,
            username=user.username,
            fullname=user.full_name,
            category="formation",
            level=level,
            pack=pack,
            capital=capital,
            message=message,
            score=score
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"""
🔥 Nouveau prospect formation

👤 Nom : {user.full_name}

🆔 ID : {user_id}

📊 Niveau : {level}

🎓 Pack : {pack}

💰 Capital : {capital}

⭐ Score : {score}

📝 Objectif :

{message}
"""
        )

        await update.message.reply_text(
            f"""
✅ Merci pour ces informations.

Votre demande a été transmise à MrTech237.

💳 Moyens de paiement :

{PAYMENT_METHODS}

MrTech237 vous contactera rapidement.
"""
        )

        context.user_data.clear()

        return
    if context.user_data.get(
        "service_request"
    ):

        await context.bot.send_message(
            ADMIN_ID,
            f"""
🤝 Nouveau service personnel

👤 {user.full_name}

🆔 {user_id}

📝 Message :

{message}
"""
        )

        await update.message.reply_text(
            """
✅ Votre demande a été transmise à MrTech237.

Vous recevrez une réponse dès que possible.
"""
        )

        context.user_data.clear()

        return
    if context.user_data.get(
        "business_request"
    ):

        await context.bot.send_message(
            ADMIN_ID,
            f"""
💼 Nouvelle opportunité commerciale

👤 {user.full_name}

🆔 {user_id}

📝 Message :

{message}
"""
        )

        await update.message.reply_text(
            """
✅ Votre proposition commerciale a été transmise à MrTech237.

Vous recevrez une réponse dès que possible.
"""
        )

        context.user_data.clear()

        return


    if context.user_data.get(
        "direct_contact"
    ):

        await context.bot.send_message(
            ADMIN_ID,
            f"""
📞 Nouvelle demande de contact direct

👤 {user.full_name}

🆔 {user_id}

📝 Message :

{message}
"""
        )

        await update.message.reply_text(
            """
✅ Votre message a été transmis à MrTech237.

Il vous répondra dès que possible.
"""
        )

        context.user_data.clear()

        return
async def prospects_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:

        return

    prospects = get_prospects()

    if not prospects:

        await update.message.reply_text(
            "Aucun prospect enregistré."
        )

        return

    text = "📊 LISTE DES PROSPECTS\n\n"

    for prospect in prospects:

        text += (
            f"👤 {prospect['fullname']}\n"
            f"⭐ Score : {prospect['score']}\n"
            f"📈 Pack : {prospect['pack']}\n"
            f"💰 Capital : {prospect['capital']}\n"
            f"----------------------\n"
        )

    await update.message.reply_text(
        text
    )
async def main():

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "prospects",
            prospects_command
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print(
        f"{BOT_NAME} lancé avec succès."
    )

    webhook_url = get_webhook_url()

    if webhook_url and os.getenv("PORT"):
        application.run_webhook(
            listen="0.0.0.0",
            port=get_port(),
            url_path=TOKEN,
            webhook_url=webhook_url,
            drop_pending_updates=True,
        )
    else:
        application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
