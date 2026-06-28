import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import config
from database import save_prospect, get_all_prospects

# Configuration des logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Dictionnaire pour suivre l'état des utilisateurs et le mode relais
user_data_storage = {}
active_relays = {} # format: {admin_id: target_user_id}

# --- FONCTIONS DE CALCUL ---
def calculate_score(pack, level):
    score = 0
    if pack == "Elite": score += 50
    elif pack == "Pro": score += 30
    else: score += 10
    
    if level == "Déjà rentable": score += 20
    return score

# --- COMMANDES ADMIN ---
async def admin_prospects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID: return
    
    prospects = get_all_prospects()
    if not prospects:
        await update.message.reply_text("Aucun prospect enregistré pour le moment.")
        return
    
    text = "📋 *Liste des prospects (Triés par score) :*\n\n"
    for p in prospects:
        text += f"ID:{p[0]} | {p[1]} | Pack: {p[2]} | Score: {p[3]} | Statut: {p[4]}\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def connect_relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID: return
    try:
        target_id = int(context.args[0])
        active_relays[config.ADMIN_ID] = target_id
        await update.message.reply_text(f"✅ Mode Relais Activé avec {target_id}. Vos messages lui seront transmis.")
    except:
        await update.message.reply_text("Utilisation : /connect ID_TELEGRAM")

async def disconnect_relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID: return
    active_relays.pop(config.ADMIN_ID, None)
    await update.message.reply_text("❌ Mode Relais Désactivé.")

# --- PARCOURS UTILISATEUR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📈 Formation Trading", callback_data="start_formation")],
        [InlineKeyboardButton("🤝 Service Personnel", callback_data="service_perso")],
        [InlineKeyboardButton("📞 Contact Direct", callback_data="contact_direct")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Bienvenue chez *{config.BOT_NAME}*.\n\nJe suis l'assistant de MrTech237. Comment puis-je vous aider ?",
        reply_markup=reply_markup, parse_mode="Markdown"
    )

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if query.data == "start_formation":
        keyboard = [
            [InlineKeyboardButton("Débutant", callback_data="lvl_Debutant"), 
             InlineKeyboardButton("Intermédiaire", callback_data="lvl_Inter")],
            [InlineKeyboardButton("Avancé", callback_data="lvl_Avance"), 
             InlineKeyboardButton("Déjà rentable", callback_data="lvl_Rentable")]
        ]
        await query.edit_message_text("Quel est votre niveau actuel ?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("lvl_"):
        user_data_storage[uid] = {"level": query.data.replace("lvl_", "")}
        keyboard = [
            [InlineKeyboardButton("Pack Starter (100$)", callback_data="pack_Starter")],
            [InlineKeyboardButton("Pack Pro (200$)", callback_data="pack_Pro")],
            [InlineKeyboardButton("Pack Elite (500$)", callback_data="pack_Elite")]
        ]
        await query.edit_message_text("Choisissez votre pack :", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("pack_"):
        user_data_storage[uid]["pack"] = query.data.replace("pack_", "")
        await query.edit_message_text("Quel est votre objectif principal (ex: Revenu complémentaire, Vivre du trading) ?")
        user_data_storage[uid]["step"] = "awaiting_goal"

# --- GESTION DES MESSAGES (RELAIS ET COLLECTE) ---
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    # 1. Mode Relais (Admin -> Client)
    if uid == config.ADMIN_ID and config.ADMIN_ID in active_relays:
        target_id = active_relays[config.ADMIN_ID]
        try:
            await context.bot.send_message(chat_id=target_id, text=f"💬 *MrTech237 :*\n{text}", parse_mode="Markdown")
        except:
            await update.message.reply_text("Impossible d'envoyer le message.")
        return

    # 2. Mode Relais (Client -> Admin)
    if uid != config.ADMIN_ID:
        # Si un relais est actif pour cet utilisateur
        for admin_id, target_id in active_relays.items():
            if target_id == uid:
                await context.bot.send_message(chat_id=admin_id, text=f"📩 *Réponse de {update.effective_user.full_name} :*\n{text}", parse_mode="Markdown")
                return

    # 3. Collecte des données du formulaire
    if uid in user_data_storage and user_data_storage[uid].get("step") == "awaiting_goal":
        data = user_data_storage[uid]
        goal = text
        score = calculate_score(data['pack'], data['level'])
        
        # Sauvegarde BDD
        save_prospect(uid, update.effective_user.username, update.effective_user.full_name, data['level'], data['pack'], goal, score)
        
        # Notification Admin
        admin_notif = (f"🔥 *Nouveau Prospect !*\n\n"
                       f"👤 Nom: {update.effective_user.full_name}\n"
                       f"🆔 ID: `{uid}`\n"
                       f"📊 Niveau: {data['level']}\n"
                       f"📦 Pack: {data['pack']}\n"
                       f"🎯 Objectif: {goal}\n"
                       f"⭐ Score: {score}")
        
        await context.bot.send_message(chat_id=config.ADMIN_ID, text=admin_notif, parse_mode="Markdown")
        
        # Réponse au client + Paiement
        await update.message.reply_text(f"Félicitations ! Votre demande pour le {data['pack']} a été reçue.")
        await update.message.reply_text(config.PAYMENT_DETAILS, parse_mode="Markdown")
        
        del user_data_storage[uid]

# --- MAIN ---
def main():
    app = Application.builder().token(config.TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prospects", admin_prospects))
    app.add_handler(CommandHandler("connect", connect_relay))
    app.add_handler(CommandHandler("disconnect", disconnect_relay))
    
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("🚀 MrTech237 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
